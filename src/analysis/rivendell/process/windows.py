#!/usr/bin/env python3 -tt
import os
import subprocess
from datetime import datetime

from rivendell.audit import write_audit_log_entry
from rivendell.memory.memory import process_memory
from rivendell.process.extractions.clipboard import extract_clipboard
from rivendell.process.extractions.evtx import extract_evtx
from rivendell.process.extractions.registry.profile import extract_registry_profile
from rivendell.process.extractions.registry.system import extract_registry_system
from rivendell.process.extractions.shimcache import extract_shimcache
from rivendell.process.extractions.usb import extract_usb
from rivendell.process.extractions.usn import extract_usn
from rivendell.process.extractions.wbem import extract_wbem
from rivendell.process.extractions.wmi import extract_wmi


def process_mft(
    verbosity, vssimage, output_directory, img, artefact, vss_path_insert, stage
):
    """Process $MFT using analyzeMFT tool from https://github.com/rowingdude/analyzeMFT"""
    if verbosity != "":
        print(
            "     Processing '{}' for {}...".format(artefact.split("/")[-1], vssimage)
        )

    entry, prnt = "{},{},{},'{}'\n".format(
        datetime.now().isoformat(),
        vssimage.replace("'", ""),
        stage,
        artefact.split("/")[-1],
    ), " -> {} -> {} '{}' from {}".format(
        datetime.now().isoformat().replace("T", " "),
        stage,
        artefact.split("/")[-1],
        vssimage,
    )
    write_audit_log_entry(verbosity, output_directory, entry, prnt)

    try:
        # Check if $MFT file exists before processing
        mft_file_path = output_directory + img.split("::")[0] + "/artefacts/raw" + vss_path_insert + "$MFT"
        if not os.path.exists(mft_file_path):
            if verbosity != "":
                print(f"     Warning: $MFT file not found at {mft_file_path}")
            return

        # Output directly to journal_mft.csv (analyzeMFT provides its own headers)
        output_csv = output_directory + img.split("::")[0] + "/artefacts/cooked" + vss_path_insert + "journal_mft.csv"

        # Run analyzeMFT.py with a CLEAN environment to avoid module conflicts
        # Only preserve PATH, completely clear PYTHONPATH and other env vars
        clean_env = {'PATH': '/usr/local/bin:/usr/bin:/bin'}

        analyze_cmd = [
            "/usr/bin/python3",
            "/opt/analyzeMFT/analyzeMFT.py",
            "-f", mft_file_path,
            "-o", output_csv,
            "--csv"
        ]

        process = subprocess.Popen(
            analyze_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=clean_env
        )
        stdout_data, stderr_data = process.communicate()

        # Check output file size
        if os.path.exists(output_csv):
            file_size = os.path.getsize(output_csv)
            if verbosity != "":
                print(f"     analyzeMFT output: {file_size:,} bytes")

        if process.returncode != 0:
            # Log the error for debugging
            stderr_text = stderr_data.decode('utf-8', errors='replace') if stderr_data else ''
            error_msg = stderr_text.replace('\n', ' ').replace(',', ';').replace("'", "")[:200]
            entry, prnt = "{},{},analyzeMFT error,'{}'\n".format(
                datetime.now().isoformat(),
                vssimage.replace("'", ""),
                error_msg
            ), " -> {} -> analyzeMFT failed for '{}': {}".format(
                datetime.now().isoformat().replace('T', ' '),
                vssimage.replace("'", ""),
                error_msg[:100]
            )
            write_audit_log_entry(verbosity, output_directory, entry, prnt)
            if verbosity != "":
                print(prnt)
            return

        if verbosity != "":
            print(f"     Successfully parsed $MFT for '{vssimage}'")

    except Exception as e:
        if verbosity != "":
            print(f"     Warning: $MFT processing failed: {e}")


def process_usn(
    verbosity, vssimage, output_directory, img, artefact, vss_path_insert, stage
):
    if verbosity != "":
        print(
            "     Processing '{}' for {}...".format(artefact.split("/")[-1], vssimage)
        )
    extract_usn(verbosity, vssimage, output_directory, img, vss_path_insert, stage, artefact)


def process_usb(
    verbosity,
    vssimage,
    output_directory,
    img,
    vss_path_insert,
    stage,
    artefact,
    jsondict,
    jsonlist,
):
    if verbosity != "":
        print(
            "     Processing '{}' for {}...".format(artefact.split("/")[-1], vssimage)
        )
    entry, prnt = "{},{},{},'{}'\n".format(
        datetime.now().isoformat(), vssimage.replace("'", ""), stage, vss_path_insert
    ), " -> {} -> {} '{}' from {}".format(
        datetime.now().isoformat().replace("T", " "),
        stage,
        artefact.split("/")[-1],
        vssimage,
    )
    write_audit_log_entry(verbosity, output_directory, entry, prnt)
    with open(artefact, encoding="ISO-8859-1") as setupapi:
        setupdata = setupapi.read()
    extract_usb(
        output_directory,
        img,
        vss_path_insert,
        jsondict,
        jsonlist,
        setupdata,
    )


def process_shimcache(
    verbosity, vssimage, output_directory, img, vss_path_insert, stage
):
    if verbosity != "":
        print("     Processing shimcache for {}...".format(vssimage))
    extract_shimcache(
        verbosity, vssimage, output_directory, img, vss_path_insert, stage
    )


def process_registry_system(
    verbosity,
    vssimage,
    output_directory,
    img,
    vss_path_insert,
    stage,
    artefact,
    jsondict,
    jsonlist,
):
    regjsonlist = []
    if not os.path.exists(
        output_directory
        + img.split("::")[0]
        + "/artefacts/cooked"
        + vss_path_insert
        + "registry/"
        + artefact.split("/")[-1]
        + ".json"
    ):
        try:
            os.makedirs(
                output_directory
                + img.split("::")[0]
                + "/artefacts/cooked"
                + vss_path_insert
                + "registry"
            )
        except:
            pass
        if verbosity != "":
            print(
                "     Processing '{}' registry hive for {}...".format(
                    artefact.split("/")[-1], vssimage
                )
            )
        entry, prnt = "{},{},{},'{}' registry hive\n".format(
            datetime.now().isoformat(),
            vssimage.replace("'", ""),
            stage,
            artefact.split("/")[-1],
        ), " -> {} -> {} registry hive '{}' from {}".format(
            datetime.now().isoformat().replace("T", " "),
            stage,
            artefact.split("/")[-1],
            vssimage,
        )
        write_audit_log_entry(verbosity, output_directory, entry, prnt)
        extract_registry_system(
            output_directory,
            img,
            vss_path_insert,
            artefact,
            jsondict,
            jsonlist,
            regjsonlist,
        )


def process_registry_profile(
    verbosity,
    vssimage,
    output_directory,
    img,
    vss_path_insert,
    stage,
    artefact,
    jsondict,
    jsonlist,
):
    regusr, regart = artefact.split("/")[-1].split("+")
    regjsonlist = []
    if not os.path.exists(
        output_directory
        + img.split("::")[0]
        + "/artefacts/cooked"
        + vss_path_insert
        + "/registry/"
        + regusr
        + "+"
        + regart
        + ".json"
    ):
        try:
            os.makedirs(
                output_directory
                + img.split("::")[0]
                + "/artefacts/cooked"
                + vss_path_insert
                + "/registry"
            )
        except:
            pass
        if verbosity != "":
            print(
                "     Processing '{}' {} registry hive for {}...".format(
                    regusr, regart, vssimage
                )
            )
        entry, prnt = "{},{},{},'{}' ({}) registry hive\n".format(
            datetime.now().isoformat(),
            vssimage.replace("'", ""),
            stage,
            regart,
            regusr,
        ), " -> {} -> {} '{}' {} registry hive from {}".format(
            datetime.now().isoformat().replace("T", " "),
            stage,
            regusr,
            regart,
            vssimage,
        )
        write_audit_log_entry(verbosity, output_directory, entry, prnt)
        extract_registry_profile(
            output_directory,
            img,
            vss_path_insert,
            artefact,
            jsondict,
            jsonlist,
            regjsonlist,
            regusr,
            regart,
        )


def process_evtx(
    verbosity,
    vssimage,
    output_directory,
    img,
    vss_path_insert,
    stage,
    artefact,
    jsondict,
    jsonlist,
):
    evtjsonlist = []
    if not os.path.exists(
        output_directory
        + img.split("::")[0]
        + "/artefacts/cooked"
        + vss_path_insert
        + "evt/"
        + artefact.split("/")[-1]
        + ".json"
    ):
        try:
            os.makedirs(
                output_directory
                + img.split("::")[0]
                + "/artefacts/cooked"
                + vss_path_insert
                + "evt"
            )
        except:
            pass
        if verbosity != "":
            print(
                "  -> processing '{}' event log for '{}'".format(
                    artefact.split("/")[-1], vssimage
                )
            )
        extract_evtx(
            verbosity,
            vssimage,
            output_directory,
            img,
            vss_path_insert,
            stage,
            artefact,
            jsondict,
            jsonlist,
            evtjsonlist,
        )


def process_clipboard(
    verbosity,
    vssimage,
    output_directory,
    img,
    vss_path_insert,
    stage,
    artefact,
    jsondict,
    jsonlist,
):
    clipjsonlist = []
    if not os.path.exists(
        output_directory
        + img.split("::")[0]
        + "/artefacts/cooked"
        + vss_path_insert
        + "clipboard/"
        + artefact.split("/")[-1]
        + ".json"
    ):
        try:
            os.makedirs(
                output_directory
                + img.split("::")[0]
                + "/artefacts/cooked"
                + vss_path_insert
                + "clipboard"
            )
        except:
            pass
        if verbosity != "":
            print(
                "     Processing '{}' ({}) clipboard evidence for {}...".format(
                    artefact.split("/")[-1].split("_")[-1],
                    artefact.split("/")[-1].split("+")[0],
                    vssimage,
                )
            )
        extract_clipboard(
            verbosity,
            vssimage,
            output_directory,
            img,
            vss_path_insert,
            stage,
            artefact,
            jsondict,
            jsonlist,
            clipjsonlist,
        )


def process_prefetch(
    verbosity,
    vssimage,
    output_directory,
    img,
    vss_path_insert,
    stage,
    mount_location,
):
    if not os.path.exists(
        output_directory
        + img.split("::")[0]
        + "/artefacts/cooked"
        + vss_path_insert
        + "prefetch"
    ):
        os.makedirs(
            output_directory
            + img.split("::")[0]
            + "/artefacts/cooked"
            + vss_path_insert
            + "prefetch"
        )
        if verbosity != "":
            print("     Processing prefetch files for {}...".format(vssimage))
        entry, prnt = "{},{},{},prefetch files\n".format(
            datetime.now().isoformat(),
            vssimage.replace("'", ""),
            stage,
        ), " -> {} -> {} prefetch files for {}".format(
            datetime.now().isoformat().replace("T", " "),
            stage,
            vssimage,
        )
        write_audit_log_entry(verbosity, output_directory, entry, prnt)

        # Check if Plaso (log2timeline) is available before attempting to use it
        plaso_available = False
        for plaso_path in ["log2timeline.py", "/opt/plaso/plaso/scripts/log2timeline.py"]:
            try:
                result = subprocess.run(["which", plaso_path], capture_output=True, timeout=5)
                if result.returncode == 0:
                    plaso_available = True
                    break
            except:
                pass

        if not plaso_available:
            entry, prnt = "{},{},{},prefetch files (skipped - Plaso not installed)\n".format(
                datetime.now().isoformat(),
                vssimage.replace("'", ""),
                stage,
            ), " -> {} -> {} prefetch files for {} (skipped - Plaso not installed)".format(
                datetime.now().isoformat().replace("T", " "),
                stage,
                vssimage,
            )
            write_audit_log_entry(verbosity, output_directory, entry, prnt)
        else:
            try:
                subprocess.Popen(
                    [
                        "log2timeline.py",
                        "--parsers",
                        "prefetch",
                        "{}/Windows/Prefetch/".format(mount_location),
                        "--storage_file",
                        output_directory
                        + img.split("::")[0]
                        + "/artefacts/cooked"
                        + vss_path_insert
                        + "prefetch/prefetch.plaso",
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                ).communicate()
                subprocess.Popen(
                    [
                        "python3",
                        "/usr/local/lib/python3.10/dist-packages/plaso/scripts/psteal.py",
                        "--source",
                        output_directory
                        + img.split("::")[0]
                        + "/artefacts/cooked"
                        + vss_path_insert
                        + "prefetch/prefetch.plaso",
                        "-o",
                        "dynamic",
                        "-w",
                        output_directory
                        + img.split("::")[0]
                        + "/artefacts/cooked"
                        + vss_path_insert
                        + "prefetch/prefetch.csv",
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                ).communicate()
            except:
                try:
                    subprocess.Popen(
                        [
                            "/opt/plaso/plaso/scripts/log2timeline.py",
                            "--parsers",
                            "prefetch",
                            "{}/Windows/Prefetch/".format(mount_location),
                            "--storage_file",
                            output_directory
                            + img.split("::")[0]
                            + "/artefacts/cooked"
                            + vss_path_insert
                            + "prefetch/prefetch.plaso",
                        ],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    ).communicate()
                    subprocess.Popen(
                        [
                            "python3",
                            "/usr/local/lib/python3.10/dist-packages/plaso/scripts/psteal.py",
                            "--source",
                            output_directory
                            + img.split("::")[0]
                            + "/artefacts/cooked"
                            + vss_path_insert
                            + "prefetch/prefetch.plaso",
                            "-o",
                            "dynamic",
                            "-w",
                            output_directory
                            + img.split("::")[0]
                            + "/artefacts/cooked"
                            + vss_path_insert
                            + "prefetch/prefetch.csv",
                        ],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    ).communicate()
                except Exception as e:
                    # If both paths fail, log and skip prefetch timeline processing
                    entry, prnt = "{},{},{},prefetch files (failed - {})\n".format(
                        datetime.now().isoformat(),
                        vssimage.replace("'", ""),
                        stage,
                        str(e),
                    ), " -> {} -> {} prefetch files for {} (failed - {})".format(
                        datetime.now().isoformat().replace("T", " "),
                        stage,
                        vssimage,
                        str(e),
                    )
                    write_audit_log_entry(verbosity, output_directory, entry, prnt)
                    pass
        if os.path.exists(
            output_directory
            + img.split("::")[0]
            + "/artefacts/cooked"
            + vss_path_insert
            + "prefetch/prefetch.plaso"
        ):
            os.remove(
                output_directory
                + img.split("::")[0]
                + "/artefacts/cooked"
                + vss_path_insert
                + "prefetch/prefetch.plaso"
            )


def process_wmi(
    verbosity,
    vssimage,
    output_directory,
    img,
    vss_path_insert,
    stage,
    artefact,
    jsondict,
    jsonlist,
):
    wmijsonlist = []
    if not os.path.exists(
        output_directory
        + img.split("::")[0]
        + "/artefacts/cooked"
        + vss_path_insert
        + "wmi/"
        + artefact.split("/")[-1]
        + ".json"
    ):
        try:
            os.makedirs(
                output_directory
                + img.split("::")[0]
                + "/artefacts/cooked"
                + vss_path_insert
                + "wmi"
            )
        except:
            pass
        if verbosity != "":
            print(
                "     Processing WMI '{}' for {}...".format(
                    artefact.split("/")[-1].split("_")[-1],
                    vssimage,
                )
            )
        extract_wmi(
            verbosity,
            vssimage,
            output_directory,
            img,
            vss_path_insert,
            stage,
            artefact,
            jsondict,
            jsonlist,
            wmijsonlist,
        )


def process_wbem(
    verbosity,
    vssimage,
    output_directory,
    img,
    vss_path_insert,
    stage,
    artefact,
):
    if not os.path.exists(
        output_directory
        + img.split("::")[0]
        + "/artefacts/cooked"
        + vss_path_insert
        + "wbem/"
        + artefact.split("/")[-1]
        + ".json"
    ):
        try:
            os.makedirs(
                output_directory
                + img.split("::")[0]
                + "/artefacts/cooked"
                + vss_path_insert
                + "wbem"
            )
        except:
            pass
        if verbosity != "":
            print(
                "     Processing WBEM '{}' for {}...".format(
                    artefact.split("/")[-1].split("_")[-1],
                    vssimage,
                )
            )
        extract_wbem(
            verbosity,
            vssimage,
            output_directory,
            img,
            vss_path_insert,
            stage,
            artefact,
        )


def process_sru(
    verbosity, vssimage, output_directory, img, vss_path_insert, stage, artefact
):
    cooked_xlsx = output_directory + img.split("::")[0] + "/artefacts/cooked" + vss_path_insert + "sru/" + artefact.split("/")[-1] + ".xlsx"
    if not os.path.exists(
        cooked_xlsx
    ):
        try:
            os.makedirs(
                output_directory
                + img.split("::")[0]
                + "/artefacts/cooked"
                + vss_path_insert
                + "sru"
            )
        except:
            pass
        if verbosity != "":
            print(
                "     Processing System Resource Utilisation database '{}' for {}...".format(
                    artefact.split("/")[-1].split("_")[-1],
                    vssimage,
                )
            )
        entry, prnt = "{},{},{},'{}' system resource utilisation database \n".format(
            datetime.now().isoformat(),
            vssimage.replace("'", ""),
            stage,
            artefact.split("/")[-1].split("_")[-1],
        ), " -> {} -> {} '{}' for {}".format(
            datetime.now().isoformat().replace("T", " "),
            stage,
            artefact.split("/")[-1].split("_")[-1],
            vssimage,
        )
        write_audit_log_entry(verbosity, output_directory, entry, prnt)
        # creating srum_dump2.py with respective artefact input and output values
        with open("/opt/elrond/elrond/tools/srum_dump/srum_dump.py") as srumdumpfile:
            srumdump = srumdumpfile.read()
        srumdump = srumdump.replace('<SRUDB.dat>', artefact).replace('<SRUM_DUMP_OUTPUT.xlsx>', cooked_xlsx)
        with open("/opt/elrond/elrond/tools/srum_dump/.srum_dump.py", "w") as srumdumpfile:
            srumdumpfile.write(srumdump)
        subprocess.Popen(
            [
                "python3",
                "/opt/elrond/elrond/tools/srum_dump/.srum_dump.py",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).communicate()
        os.remove("/opt/elrond/elrond/tools/srum_dump/.srum_dump.py")
        # cooked_csv = output_directory + img.split("::")[0] + "/artefacts/cooked" + vss_path_insert + "sru/" + artefact.split("/")[-1] + ".csv"
        # cooked_json = output_directory + img.split("::")[0] + "/artefacts/cooked" + vss_path_insert + "sru/" + artefact.split("/")[-1] + ".json"
        # read from "/opt/elrond/elrond/tools/srum-dump/SRUM_TEMPLATE2.XLSX" using pandas to then convert into csv/json


def process_ual(
    verbosity, vssimage, output_directory, img, vss_path_insert, stage, artefact
):
    if not os.path.exists(
        output_directory
        + img.split("::")[0]
        + "/artefacts/cooked"
        + vss_path_insert
        + "ual/"
        + artefact.split("/")[-1]
        + ".csv"
    ):
        try:
            os.makedirs(
                output_directory
                + img.split("::")[0]
                + "/artefacts/cooked"
                + vss_path_insert
                + "ual"
            )
        except:
            pass
        if verbosity != "":
            print(
                "     Processing User Access Log '{}' for {}...".format(
                    artefact.split("/")[-1].split("_")[-1],
                    vssimage,
                )
            )
        entry, prnt = "{},{},{},'{}' user access log \n".format(
            datetime.now().isoformat(),
            vssimage.replace("'", ""),
            stage,
            artefact.split("/")[-1].split("_")[-1],
        ), " -> {} -> {} '{}' for {}".format(
            datetime.now().isoformat().replace("T", " "),
            stage,
            artefact.split("/")[-1].split("_")[-1],
            vssimage,
        )
        write_audit_log_entry(verbosity, output_directory, entry, prnt)
        try:
            kstrike_list = str(
                subprocess.Popen(
                    [
                        "python3",
                        "/opt/elrond/elrond/tools/KStrike/KStrike.py",
                        artefact,
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                ).communicate()[0]
            )[2:-4].split("\\r\\n")
            if len(kstrike_list) > 0:
                with open(
                    output_directory
                    + img.split("::")[0]
                    + "/artefacts/cooked"
                    + vss_path_insert
                    + "ual/"
                    + artefact.split("/")[-1]
                    + ".csv",
                    "a",
                ) as ual_csv:
                    ual_csv.write(
                        "{},LastWriteTime\n".format(
                            kstrike_list[0][0:-4].replace(",", "").replace("||", ","),
                        )
                    )
                    for ual_entry in kstrike_list[1:]:
                        ual_csv.write(
                            "{},{}\n".format(
                                ual_entry[0:-4].replace(",", "").replace("||", ","),
                                ual_entry.split("||")[4],
                            )
                        )
        except KeyError as error:
            entry, prnt = "{},{},{},'{}' user access log [{}]\n".format(
                error,
                datetime.now().isoformat(),
                vssimage.replace("'", ""),
                stage,
                artefact.split("/")[-1].split("_")[-1],
            ), " -> {} -> {} '{}' experienced {} for {}".format(
                datetime.now().isoformat().replace("T", " "),
                stage,
                artefact.split("/")[-1].split("_")[-1],
                error,
                vssimage,
            )
            write_audit_log_entry(verbosity, output_directory, entry, prnt)


def process_jumplists(
    verbosity, vssimage, output_directory, img, vss_path_insert, stage, artefact
):
    if not os.path.exists(
        output_directory
        + img.split("::")[0]
        + "/artefacts/cooked"
        + vss_path_insert
        + "jumplists.csv"
    ):
        with open(
            output_directory
            + img.split("::")[0]
            + "/artefacts/cooked"
            + vss_path_insert
            + "jumplists.csv",
            "a",
        ) as jumplistcsv:
            jumplistcsv.write("Device,Account,JumplistID,JumplistType\n")
    else:
        with open(
            output_directory
            + img.split("::")[0]
            + "/artefacts/cooked"
            + vss_path_insert
            + "jumplists.csv",
            "a",
        ) as jumplistcsv:
            if os.path.exists(
                output_directory
                + img.split("::")[0]
                + "/artefacts/cooked"
                + vss_path_insert
                + "jumplists.csv"
            ):
                if verbosity != "":
                    print(
                        "     Processing Jumplist file '{}' ({}) for {}...".format(
                            artefact.split("+")[1],
                            artefact.split("/")[-1].split("+")[0],
                            vssimage,
                        )
                    )
                (
                    entry,
                    prnt,
                ) = "{},{},{},'{}' ({}) jumplist file\n".format(
                    datetime.now().isoformat(),
                    vssimage.replace("'", ""),
                    stage,
                    artefact.split("+")[1],
                    artefact.split("/")[-1].split("+")[0],
                ), " -> {} -> {} jumplist file '{}' ({}) from {}".format(
                    datetime.now().isoformat().replace("T", " "),
                    stage,
                    artefact.split("+")[1],
                    artefact.split("/")[-1].split("+")[0],
                    vssimage,
                )
                write_audit_log_entry(verbosity, output_directory, entry, prnt)
                jumplistcsv.write(
                    img.split("::")[0]
                    + ","
                    + artefact.split("/")[-1].split("+")[0]
                    + ","
                    + artefact.split("+")[1].split(".")[0]
                    + ","
                    + artefact.split("+")[1].split(".")[1]
                    + "\n"
                )


def process_outlook(
    verbosity, vssimage, output_directory, img, vss_path_insert, stage, artefact
):
    if verbosity != "":
        print(
            "     Processing Outlook file '{}' ({}) for {}...".format(
                artefact.split("/")[-1],
                artefact.split("/")[-2],
                vssimage,
            )
        )
    (
        entry,
        prnt,
    ) = "{},{},{},'{}' ({}) outlook file\n".format(
        datetime.now().isoformat(),
        vssimage.replace("'", ""),
        stage,
        artefact.split("/")[-1],
        artefact.split("/")[-2],
    ), " -> {} -> {} outlook file '{}' ({}) from {}".format(
        datetime.now().isoformat().replace("T", " "),
        stage,
        artefact.split("/")[-1],
        artefact.split("/")[-2],
        vssimage,
    )
    write_audit_log_entry(verbosity, output_directory, entry, prnt)
    if not os.path.exists(os.path.join(artefact.split(".pst")[0])):
        subprocess.Popen(
            [
                "sudo",
                "readpst",
                artefact,
                "-D",
                "-S",
                "-o",
                "/".join(os.path.join(artefact.split(".pst")[0]).split("/")[:-1]),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).communicate()


def process_hiberfil(
    d,
    verbosity,
    vssimage,
    output_directory,
    img,
    vss_path_insert,
    stage,
    artefact,
    volchoice,
    vss,
    vssmem,
    memtimeline,
):
    if verbosity != "":
        print(
            "     Processing '{}' for {}...".format(artefact.split("/")[-1], vssimage)
        )
    os.makedirs(
        output_directory
        + img.split("::")[0]
        + "/artefacts/cooked"
        + vss_path_insert
        + "memory"
    )
    profile, vssmem = process_memory(
        output_directory,
        verbosity,
        d,
        stage,
        img,
        artefact,
        volchoice,
        vss,
        vssmem,
        memtimeline,
    )
    return profile, vssmem


def process_pagefile(
    verbosity, vssimage, output_directory, img, vss_path_insert, artefact
):
    if not os.path.exists(
        output_directory
        + img.split("::")[0]
        + "/artefacts/cooked"
        + vss_path_insert
        + "memory"
    ):
        if verbosity != "":
            print(
                "     Processing '{}' for {}...".format(
                    artefact.split("/")[-1], vssimage
                )
            )
        os.makedirs(
            output_directory
            + img.split("::")[0]
            + "/artefacts/cooked"
            + vss_path_insert
            + "memory"
        )
        entry, prnt = "{},{},extracting strings,'{}'\n".format(
            datetime.now().isoformat(),
            vssimage,
            artefact.split("/")[-1],
        ), " -> {} -> extracting strings from '{}' from {}".format(
            datetime.now().isoformat().replace("T", " "),
            artefact.split("/")[-1],
            vssimage,
        )
        write_audit_log_entry(verbosity, output_directory, entry, prnt)
        subprocess.Popen(
            [
                "strings",
                artefact,
                ">>",
                output_directory
                + img.split("::")[0]
                + "/artefacts/cooked"
                + vss_path_insert
                + "memory/"
                + artefact.split("/")[-1]
                + ".strings",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).communicate()[0]
        (
            entry,
            prnt,
        ) = "{},{},extraction of strings complete,'{}'\n".format(
            datetime.now().isoformat(),
            vssimage,
            artefact.split("/")[-1],
        ), " -> {} -> extraction of strings from '{}' completed from {}".format(
            datetime.now().isoformat().replace("T", " "),
            artefact.split("/")[-1],
            vssimage,
        )
