// Rivendell.app: shows Rivendell's web UI in its own window, starting the Docker stack
// through the launcher when the UI isn't answering. Setup.swift handles the first run
// (container runtime, where Rivendell's files live, evidence folders) and updates.
import AppKit
import WebKit

let frontendURL = URL(string: "http://localhost:5687")!
let startTimeout: TimeInterval = 900

enum Page { case splash, setup, ui }

@main
final class AppDelegate: NSObject, NSApplicationDelegate, WKNavigationDelegate, WKUIDelegate,
                         WKDownloadDelegate, WKScriptMessageHandler {
    var window: NSWindow!
    var webView: WKWebView!
    var page = Page.splash
    var pageReady = false
    var pageQueue: [String] = []
    let setup = SetupState()
    var runtimeTimer: Timer?
    var orbObservation: NSKeyValueObservation?

    static func main() {
        let app = NSApplication.shared
        let delegate = AppDelegate()
        app.delegate = delegate
        app.setActivationPolicy(.regular)
        app.run()
    }

    var appVersion: String {
        Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String ?? "0"
    }

    /// The source tree a release build carries, unpacked by setup into the user's chosen folder
    var bundledSource: URL? {
        Bundle.main.url(forResource: "rivendell-src", withExtension: "tar.gz")
    }

    /// The Rivendell copy to run: RIVENDELL_ROOT, then the one chosen in setup, then the
    /// checkout a local build (`rivendell app install`) was made from
    var root: String? {
        [ProcessInfo.processInfo.environment["RIVENDELL_ROOT"],
         UserDefaults.standard.string(forKey: "RivendellRoot"),
         Bundle.main.object(forInfoDictionaryKey: "RivendellRoot") as? String]
            .compactMap { $0 }
            .first(where: isRivendellCopy)
    }

    func applicationDidFinishLaunching(_ notification: Notification) {
        buildMenu()
        let config = WKWebViewConfiguration()
        config.userContentController.add(self, name: "rivendell")
        webView = WKWebView(frame: .zero, configuration: config)
        webView.navigationDelegate = self
        webView.uiDelegate = self
        webView.allowsBackForwardNavigationGestures = true

        window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 1440, height: 900),
                          styleMask: [.titled, .closable, .miniaturizable, .resizable],
                          backing: .buffered, defer: false)
        window.title = "Rivendell"
        window.contentView = webView
        window.center()
        window.setFrameAutosaveName("RivendellMain")
        window.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)

        launch()
    }

    func applicationShouldHandleReopen(_ sender: NSApplication, hasVisibleWindows: Bool) -> Bool {
        if !hasVisibleWindows { window.makeKeyAndOrderFront(nil) }
        return true
    }

    // MARK: Starting the stack

    func launch() {
        guard let root = root else {
            showSetup()
            return
        }
        if needsUpdate(root) {
            askToUpdate(root)
        } else {
            startOrShow()
        }
    }

    func startOrShow() {
        showSplash()
        probe { up in
            if up { self.showUI() } else { self.startStack() }
        }
    }

    func probe(_ done: @escaping (Bool) -> Void) {
        var request = URLRequest(url: frontendURL, cachePolicy: .reloadIgnoringLocalCacheData, timeoutInterval: 2)
        request.httpMethod = "HEAD"
        URLSession.shared.dataTask(with: request) { _, response, _ in
            DispatchQueue.main.async { done(response is HTTPURLResponse) }
        }.resume()
    }

    func startStack() {
        splashStatus("Starting the Docker stack…")
        runLauncher(["start"], output: splashLine) { status in
            guard status == 0 else {
                self.splashError("'rivendell start' exited with status \(status). The output is above.")
                return
            }
            self.splashStatus("Waiting for the web UI on \(frontendURL.host!):\(frontendURL.port!)…")
            self.waitForUI(deadline: Date().addingTimeInterval(startTimeout))
        }
    }

    func waitForUI(deadline: Date) {
        probe { up in
            if up {
                self.showUI()
            } else if Date() > deadline {
                self.splashError("The stack started but nothing answered on \(frontendURL) after \(Int(startTimeout / 60)) minutes. Try 'rivendell status'.")
            } else {
                DispatchQueue.main.asyncAfter(deadline: .now() + 2) { self.waitForUI(deadline: deadline) }
            }
        }
    }

    /// Runs `rivendell <args>` with a PATH that finds Docker from a GUI launch, passing
    /// each line of output to `output` and the exit status to `completion` (main thread).
    func runLauncher(_ args: [String], output: @escaping (String) -> Void,
                     completion: @escaping (Int32) -> Void) {
        guard let root = root else {
            showSetup()
            return
        }
        let process = Process()
        process.executableURL = URL(fileURLWithPath: "/bin/bash")
        process.arguments = ["\(root)/rivendell"] + args
        process.currentDirectoryURL = URL(fileURLWithPath: root)
        process.environment = processEnvironment()

        let pipe = Pipe()
        process.standardOutput = pipe
        process.standardError = pipe
        pipe.fileHandleForReading.readabilityHandler = { handle in
            let data = handle.availableData
            guard !data.isEmpty, let text = String(data: data, encoding: .utf8) else { return }
            DispatchQueue.main.async {
                text.split(whereSeparator: \.isNewline).forEach { output(String($0)) }
            }
        }
        process.terminationHandler = { p in
            pipe.fileHandleForReading.readabilityHandler = nil
            DispatchQueue.main.async { completion(p.terminationStatus) }
        }
        do {
            try process.run()
        } catch {
            output("Couldn't run \(root)/rivendell: \(error.localizedDescription)")
            completion(-1)
        }
    }

    // MARK: Pages: splash, setup, the UI

    func show(_ newPage: Page) {
        page = newPage
        pageReady = false
        pageQueue = []
        if newPage != .setup {
            runtimeTimer?.invalidate()
            runtimeTimer = nil
        }
    }

    func showSplash() {
        show(.splash)
        let html = """
        <!doctype html><html><head><meta charset="utf-8"><style>
        :root { color-scheme: dark; }
        body { margin: 0; height: 100vh; display: flex; flex-direction: column; align-items: center;
               justify-content: center; background: #0b1210; color: #b9c9b4;
               font: 14px -apple-system, system-ui, sans-serif; }
        img { width: 420px; max-width: 70vw; }
        #status { margin: 18px 0 10px; font-size: 15px; }
        #status.error { color: #e8a07a; }
        pre { width: min(900px, 90vw); height: 32vh; overflow: auto; margin: 0; padding: 12px;
              background: #050908; border: 1px solid #1d2b26; border-radius: 6px;
              font: 12px "JetBrains Mono", Menlo, monospace; color: #8fa58a; white-space: pre-wrap; }
        button { margin-top: 14px; padding: 6px 18px; background: #1d3a2e; color: #d6e6d0;
                 border: 1px solid #2f5a47; border-radius: 6px; font: inherit; cursor: pointer; display: none; }
        </style></head><body>
        <img src="rivendell.png" alt="Rivendell">
        <div id="status">Checking whether Rivendell is running…</div>
        <pre id="log"></pre>
        <button id="retry" onclick="webkit.messageHandlers.rivendell.postMessage('retry')">Try again</button>
        <script>
        function line(t) { const l = document.getElementById('log'); l.textContent += t + '\\n'; l.scrollTop = l.scrollHeight; }
        function status(t, error) { const s = document.getElementById('status'); s.textContent = t;
          s.className = error ? 'error' : ''; document.getElementById('retry').style.display = error ? 'inline-block' : 'none'; }
        </script></body></html>
        """
        webView.loadHTMLString(html, baseURL: Bundle.main.resourceURL)
    }

    /// Calls a function on the splash or setup page, holding calls until the page has loaded.
    func js(_ function: String, _ args: [Any]) {
        guard page != .ui, let data = try? JSONSerialization.data(withJSONObject: args),
              let json = String(data: data, encoding: .utf8) else { return }
        let call = "\(function)(...\(json))"
        if pageReady { webView.evaluateJavaScript(call) } else { pageQueue.append(call) }
    }

    func splashLine(_ text: String) { js("line", [text]) }
    func splashStatus(_ text: String) { js("status", [text, false]) }
    func splashError(_ text: String) { js("status", [text, true]) }

    func showUI() {
        show(.ui)
        webView.load(URLRequest(url: frontendURL))
    }

    func userContentController(_ controller: WKUserContentController, didReceive message: WKScriptMessage) {
        if message.body as? String == "retry" {
            launch()
        } else if page == .setup, let body = message.body as? [String: Any] {
            setupMessage(body)
        }
    }

    // MARK: Menu actions

    @objc func openInBrowser(_ sender: Any?) {
        NSWorkspace.shared.open(page == .ui ? webView.url ?? frontendURL : frontendURL)
    }

    @objc func stopStack(_ sender: Any?) {
        stopThen { self.js("status", ["Rivendell is stopped. Rivendell › Start Rivendell (⇧⌘S) brings it back.", false]) }
    }

    @objc func stopAndQuit(_ sender: Any?) {
        stopThen { NSApp.terminate(nil) }
    }

    @objc func startStackMenu(_ sender: Any?) { launch() }

    @objc func setupMenu(_ sender: Any?) { showSetup() }

    @objc func reload(_ sender: Any?) {
        switch page {
        case .ui: webView.reload()
        case .setup: showSetup()
        case .splash: launch()
        }
    }

    func stopThen(_ next: @escaping () -> Void) {
        guard root != nil else {
            next()
            return
        }
        showSplash()
        splashStatus("Stopping the Docker stack…")
        runLauncher(["stop"], output: splashLine) { _ in next() }
    }

    func buildMenu() {
        let main = NSMenu()

        let appItem = NSMenuItem()
        let appMenu = NSMenu()
        appMenu.addItem(withTitle: "About Rivendell", action: #selector(NSApplication.orderFrontStandardAboutPanel(_:)), keyEquivalent: "")
        appMenu.addItem(withTitle: "Set Up Rivendell…", action: #selector(setupMenu(_:)), keyEquivalent: ",")
        appMenu.addItem(.separator())
        appMenu.addItem(withTitle: "Hide Rivendell", action: #selector(NSApplication.hide(_:)), keyEquivalent: "h")
        let others = appMenu.addItem(withTitle: "Hide Others", action: #selector(NSApplication.hideOtherApplications(_:)), keyEquivalent: "h")
        others.keyEquivalentModifierMask = [.command, .option]
        appMenu.addItem(.separator())
        let stopQuit = appMenu.addItem(withTitle: "Stop Rivendell and Quit", action: #selector(stopAndQuit(_:)), keyEquivalent: "q")
        stopQuit.keyEquivalentModifierMask = [.command, .option]
        appMenu.addItem(withTitle: "Quit Rivendell", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q")
        appItem.submenu = appMenu
        main.addItem(appItem)

        // Without an Edit menu, copy and paste don't reach the web view
        let editItem = NSMenuItem()
        let editMenu = NSMenu(title: "Edit")
        editMenu.addItem(withTitle: "Undo", action: Selector(("undo:")), keyEquivalent: "z")
        editMenu.addItem(withTitle: "Redo", action: Selector(("redo:")), keyEquivalent: "Z")
        editMenu.addItem(.separator())
        editMenu.addItem(withTitle: "Cut", action: #selector(NSText.cut(_:)), keyEquivalent: "x")
        editMenu.addItem(withTitle: "Copy", action: #selector(NSText.copy(_:)), keyEquivalent: "c")
        editMenu.addItem(withTitle: "Paste", action: #selector(NSText.paste(_:)), keyEquivalent: "v")
        editMenu.addItem(withTitle: "Select All", action: #selector(NSText.selectAll(_:)), keyEquivalent: "a")
        editItem.submenu = editMenu
        main.addItem(editItem)

        let viewItem = NSMenuItem()
        let viewMenu = NSMenu(title: "View")
        viewMenu.addItem(withTitle: "Reload", action: #selector(reload(_:)), keyEquivalent: "r")
        viewMenu.addItem(withTitle: "Back", action: #selector(WKWebView.goBack(_:)), keyEquivalent: "[")
        viewMenu.addItem(withTitle: "Forward", action: #selector(WKWebView.goForward(_:)), keyEquivalent: "]")
        viewMenu.addItem(.separator())
        let fullScreen = viewMenu.addItem(withTitle: "Enter Full Screen", action: #selector(NSWindow.toggleFullScreen(_:)), keyEquivalent: "f")
        fullScreen.keyEquivalentModifierMask = [.command, .control]
        viewItem.submenu = viewMenu
        main.addItem(viewItem)

        let stackItem = NSMenuItem()
        let stackMenu = NSMenu(title: "Rivendell")
        stackMenu.addItem(withTitle: "Open in Browser", action: #selector(openInBrowser(_:)), keyEquivalent: "o")
        stackMenu.addItem(.separator())
        stackMenu.addItem(withTitle: "Start Rivendell", action: #selector(startStackMenu(_:)), keyEquivalent: "S")
        stackMenu.addItem(withTitle: "Stop Rivendell", action: #selector(stopStack(_:)), keyEquivalent: "")
        stackItem.submenu = stackMenu
        main.addItem(stackItem)

        let windowItem = NSMenuItem()
        let windowMenu = NSMenu(title: "Window")
        windowMenu.addItem(withTitle: "Minimise", action: #selector(NSWindow.miniaturize(_:)), keyEquivalent: "m")
        windowMenu.addItem(withTitle: "Close", action: #selector(NSWindow.performClose(_:)), keyEquivalent: "w")
        windowItem.submenu = windowMenu
        main.addItem(windowItem)
        NSApp.windowsMenu = windowMenu

        NSApp.mainMenu = main
    }

    // MARK: Navigation, downloads, pop-ups

    func webView(_ webView: WKWebView, decidePolicyFor action: WKNavigationAction,
                 decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        if action.shouldPerformDownload {
            decisionHandler(.download)
            return
        }
        // Links off the frontend (Splunk, Kibana, ATT&CK, GitHub) go to the default browser
        if let url = action.request.url, action.navigationType == .linkActivated,
           url.host != frontendURL.host || url.port != frontendURL.port {
            NSWorkspace.shared.open(url)
            decisionHandler(.cancel)
            return
        }
        decisionHandler(.allow)
    }

    func webView(_ webView: WKWebView, decidePolicyFor response: WKNavigationResponse,
                 decisionHandler: @escaping (WKNavigationResponsePolicy) -> Void) {
        let disposition = (response.response as? HTTPURLResponse)?.value(forHTTPHeaderField: "Content-Disposition") ?? ""
        decisionHandler(!response.canShowMIMEType || disposition.lowercased().hasPrefix("attachment") ? .download : .allow)
    }

    func webView(_ webView: WKWebView, navigationAction: WKNavigationAction, didBecome download: WKDownload) {
        download.delegate = self
    }

    func webView(_ webView: WKWebView, navigationResponse: WKNavigationResponse, didBecome download: WKDownload) {
        download.delegate = self
    }

    func download(_ download: WKDownload, decideDestinationUsing response: URLResponse,
                  suggestedFilename: String, completionHandler: @escaping (URL?) -> Void) {
        let downloads = FileManager.default.urls(for: .downloadsDirectory, in: .userDomainMask)[0]
        let base = (suggestedFilename as NSString).deletingPathExtension
        let ext = (suggestedFilename as NSString).pathExtension
        var target = downloads.appendingPathComponent(suggestedFilename)
        var n = 1
        while FileManager.default.fileExists(atPath: target.path) {
            target = downloads.appendingPathComponent(ext.isEmpty ? "\(base) (\(n))" : "\(base) (\(n)).\(ext)")
            n += 1
        }
        completionHandler(target)
    }

    func downloadDidFinish(_ download: WKDownload) {
        NSApp.requestUserAttention(.informationalRequest)
    }

    func webView(_ webView: WKWebView, createWebViewWith configuration: WKWebViewConfiguration,
                 for action: WKNavigationAction, windowFeatures: WKWindowFeatures) -> WKWebView? {
        // target="_blank": the frontend's own pages stay in the window, anything else opens in the browser
        if let url = action.request.url {
            if url.host == frontendURL.host && url.port == frontendURL.port {
                webView.load(action.request)
            } else {
                NSWorkspace.shared.open(url)
            }
        }
        return nil
    }

    func webView(_ webView: WKWebView, runJavaScriptAlertPanelWithMessage message: String,
                 initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping () -> Void) {
        let alert = NSAlert()
        alert.messageText = message
        alert.beginSheetModal(for: window) { _ in completionHandler() }
    }

    func webView(_ webView: WKWebView, runJavaScriptConfirmPanelWithMessage message: String,
                 initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping (Bool) -> Void) {
        let alert = NSAlert()
        alert.messageText = message
        alert.addButton(withTitle: "OK")
        alert.addButton(withTitle: "Cancel")
        alert.beginSheetModal(for: window) { completionHandler($0 == .alertFirstButtonReturn) }
    }

    func webView(_ webView: WKWebView, runJavaScriptTextInputPanelWithPrompt prompt: String,
                 defaultText: String?, initiatedByFrame frame: WKFrameInfo,
                 completionHandler: @escaping (String?) -> Void) {
        let alert = NSAlert()
        alert.messageText = prompt
        let field = NSTextField(frame: NSRect(x: 0, y: 0, width: 300, height: 24))
        field.stringValue = defaultText ?? ""
        alert.accessoryView = field
        alert.addButton(withTitle: "OK")
        alert.addButton(withTitle: "Cancel")
        alert.beginSheetModal(for: window) { completionHandler($0 == .alertFirstButtonReturn ? field.stringValue : nil) }
    }

    func webView(_ webView: WKWebView, runOpenPanelWith parameters: WKOpenPanelParameters,
                 initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping ([URL]?) -> Void) {
        let panel = NSOpenPanel()
        panel.allowsMultipleSelection = parameters.allowsMultipleSelection
        panel.canChooseDirectories = parameters.allowsDirectories
        panel.beginSheetModal(for: window) { completionHandler($0 == .OK ? panel.urls : nil) }
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        guard page != .ui else { return }
        pageReady = true
        pageQueue.forEach { webView.evaluateJavaScript($0) }
        pageQueue = []
    }

    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
        lostUI(error)
    }

    func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
        lostUI(error)
    }

    func lostUI(_ error: Error) {
        // The stack went away under us (stopped elsewhere, Docker quit): back to the splash
        guard page == .ui, (error as NSError).domain == NSURLErrorDomain else { return }
        showSplash()
        splashError("Lost the web UI: \(error.localizedDescription)")
    }
}
