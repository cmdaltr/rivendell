#!/usr/bin/env python3 -tt
import os
import shutil
import time
from datetime import datetime
from zipfile import ZipFile

from rivendell.audit import write_audit_log_entry


def archive_artefacts(verbosity, output_directory):
    stage = "archiving"
    print(
        "\n\n  -> \033[1;36mCommencing Archive Phase...\033[1;m\n  ----------------------------------------"
    )

    # Get case name from output_directory (remove trailing slash)
    case_dir = output_directory.rstrip("/")
    case_name = case_dir.split("/")[-1]
    # Archive goes alongside the case directory (in parent)
    parent_dir = "/".join(case_dir.split("/")[:-1]) + "/"
    archive_path = parent_dir + case_name + ".zip"

    print("    Archiving case '{}'...".format(case_name))
    entry, prnt = "{},{},{},commenced\n".format(
        datetime.now().isoformat(), case_name, stage
    ), " -> {} -> {} case '{}'".format(
        datetime.now().isoformat().replace("T", " "),
        stage,
        case_name,
    )
    write_audit_log_entry(verbosity, output_directory, entry, prnt)

    print("     Creating archive at '{}'...".format(archive_path))
    z = ZipFile(archive_path, "w")
    skipped_files = 0
    for ziproot, _, zipfiles in os.walk(output_directory):
        for zf in zipfiles:
            # Skip macOS metadata files (._* AppleDouble files)
            if zf.startswith("._"):
                skipped_files += 1
                continue

            filepath = os.path.join(ziproot, zf)
            # Exclude the archive itself
            if filepath != archive_path:
                try:
                    # Store with relative path from case directory
                    arcname = os.path.relpath(filepath, output_directory)
                    z.write(filepath, arcname)
                except (OSError, IOError, PermissionError) as e:
                    # Log permission errors but continue archiving
                    if verbosity >= 1:
                        print(f"     Warning: Could not archive '{zf}': {e}")
                    skipped_files += 1
    z.close()

    if skipped_files > 0:
        print(f"     Skipped {skipped_files} file(s) due to permissions or metadata")

    print("  -> Completed Archiving Phase for case '{}'".format(case_name))
    entry, prnt = "{},{},{},completed\n".format(
        datetime.now().isoformat(), case_name, stage
    ), " -> {} -> archiving completed for case '{}'".format(
        datetime.now().isoformat().replace("T", " "),
        case_name,
    )
    write_audit_log_entry(verbosity, output_directory, entry, prnt)
    print(
        "  ----------------------------------------\n  -> Completed Archiving Phase.\n"
    )
    time.sleep(1)


def delete_artefacts(verbosity, output_directory):
    stage = "deleting"
    print(
        "\n\n  -> \033[1;36mCommencing Deletion Phase...\033[1;m\n  ----------------------------------------"
    )
    dlist = []
    for each in os.listdir(output_directory):
        if os.path.exists(output_directory + each + "/artefacts"):
            dlist.append(output_directory + each)
    for deach in dlist:
        print("    Deleting artefacts for {}...".format(deach.split("/")[-1]))
        entry, prnt = "{},{},{},commenced\n".format(
            datetime.now().isoformat(), deach.split("/")[-1], stage
        ), " -> {} -> {} artefacts for '{}'".format(
            datetime.now().isoformat().replace("T", " "),
            stage,
            deach.split("/")[-1],
        )
        write_audit_log_entry(verbosity, output_directory, entry, prnt)
        print("     Deleting files for '{}'...".format(deach.split("/")[-1]))
        for droot, ddir, dfile in os.walk(deach):
            for eachdir in ddir:
                name = droot + "/" + eachdir
                if not name.endswith(deach):
                    shutil.rmtree(droot + "/" + eachdir)
            for eachfile in dfile:
                name = droot + "/" + eachfile
                if not name.endswith(
                    deach.split("/")[-1] + "/" + deach.split("/")[-1] + ".log"
                ) and not name.endswith(
                    deach.split("/")[-1] + "/" + deach.split("/")[-1] + ".zip"
                ):
                    os.remove(droot + "/" + eachfile)
        print("  -> Completed Deletion Phase for {}".format(deach.split("/")[-1]))
        entry, prnt = "{},{},{},completed\n".format(
            datetime.now().isoformat(), deach.split("/")[-1], stage
        ), " -> {} -> deletion completed for '{}'".format(
            datetime.now().isoformat().replace("T", " "),
            deach.split("/")[-1],
        )
        write_audit_log_entry(verbosity, output_directory, entry, prnt)
        print(
            "  ----------------------------------------\n  -> Completed Deletion Phase.\n"
        )
        time.sleep(1)


def cleanup_small_files_and_empty_dirs(output_directory, min_file_size=10):
    """
    Clean up small files (<10 bytes) and empty directories after processing.

    This removes artifacts that are effectively empty or contain no useful data.
    Also removes macOS metadata files (._* AppleDouble files).

    Args:
        output_directory: Base output directory to clean
        min_file_size: Minimum file size in bytes (files smaller than this are deleted)

    Returns:
        Tuple of (deleted_files_count, deleted_dirs_count)
    """
    deleted_files = 0
    deleted_dirs = 0

    print(f" -> {datetime.now().isoformat().replace('T', ' ')} -> cleaning up small files and empty directories...")

    # First pass: delete small files and macOS metadata files
    for root, dirs, files in os.walk(output_directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            try:
                # Delete macOS AppleDouble metadata files (._*)
                if filename.startswith("._"):
                    os.remove(filepath)
                    deleted_files += 1
                    continue

                # Delete small files
                file_size = os.path.getsize(filepath)
                if file_size < min_file_size:
                    os.remove(filepath)
                    deleted_files += 1
            except (OSError, IOError):
                pass

    # Second pass: delete empty directories (bottom-up)
    # We need to walk bottom-up so we can delete nested empty dirs
    for root, dirs, files in os.walk(output_directory, topdown=False):
        for dirname in dirs:
            dirpath = os.path.join(root, dirname)
            try:
                # Only delete if directory is empty
                if not os.listdir(dirpath):
                    os.rmdir(dirpath)
                    deleted_dirs += 1
            except (OSError, IOError):
                pass

    if deleted_files > 0 or deleted_dirs > 0:
        print(f"     Cleaned up {deleted_files} small files and {deleted_dirs} empty directories")

    return deleted_files, deleted_dirs
