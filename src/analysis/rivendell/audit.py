#!/usr/bin/env python3 -tt
import os
from datetime import datetime


def write_audit_log_entry(verbosity, output_directory, entry, prnt):
    if "LastWriteTime,elrond_host,elrond_stage,elrond_log_entry\n" in entry:
        writemode = "w"
    else:
        writemode = "a"

    # Write audit log at case level (output_directory), not per-image
    audit_log_path = os.path.join(output_directory.rstrip('/'), "rivendell_audit.log")

    with open(audit_log_path, writemode) as logentry:
        logentry.write(entry.replace("'", ""))
    if prnt != "":
        print(prnt)


def manage_error(output_directory, verbosity, error, state, img, item, vsstext):
    entry, prnt = "{},{},{} failed ({}),'{}'\n".format(
        datetime.now().isoformat(),
        img.split("::")[0],
        state,
        str(error).split("] ")[-1],
        item.strip("/").split("/")[-1],
    ), " -> {} -> ERROR - {}: {}; {} failed for '{}'{} from '{}'".format(
        datetime.now().isoformat().replace("T", " "),
        str(error).split("] ")[-1].split(": ")[0],
        "'" + str(error).split("] ")[-1].split(": ")[1].strip("'")[-24:-4] + "'",
        state,
        item.strip("/").split("/")[-1],
        vsstext.replace("vss", "volume shadow copy #"),
        img.split("::")[0],
    )
    write_audit_log_entry(verbosity, output_directory, entry, prnt)
