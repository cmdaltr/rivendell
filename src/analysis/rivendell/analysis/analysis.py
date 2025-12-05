#!/usr/bin/env python3 -tt

import json
import os
import re
import time
from datetime import datetime

from rivendell.audit import write_audit_log_entry
from rivendell.analysis.iocs import compare_iocs


def _analyse_artemis_mft_from_status_log(ar, f, stage, vssimage, anysd, verbosity, output_directory, analyse_mft_json_func):
    """
    Parse Artemis status.log to find MFT artifact files and analyze them.

    Artemis outputs files with UUID names (e.g., 68330d32-c35e-4d43-8655-1cb5e9d90b83.jsonl)
    and creates a status.log mapping file in the format:
    "artifact_name:uuid.jsonl"

    This function finds MFT/rawfiles artifacts and analyzes them.
    """
    try:
        status_log_path = os.path.join(ar, f)
        print(" -> {} -> found Artemis status.log, checking for MFT data...".format(
            datetime.now().isoformat().replace("T", " ")
        ))
        with open(status_log_path, 'r', encoding='utf-8', errors='replace') as log_file:
            for line in log_file:
                line = line.strip()
                if not line:
                    continue
                # Format: "mft:uuid.jsonl" or "rawfiles:uuid.jsonl"
                if ':' in line:
                    artifact_type, filename = line.split(':', 1)
                    # Look for MFT-related artifacts
                    if artifact_type.lower() in ('mft', 'rawfiles', 'filelisting'):
                        artifact_path = os.path.join(ar, filename.strip('"').strip())
                        if os.path.exists(artifact_path):
                            print(" -> {} -> found MFT artifact: {}".format(
                                datetime.now().isoformat().replace("T", " "),
                                os.path.basename(artifact_path)
                            ))
                            analyse_mft_json_func(stage, vssimage, artifact_path, anysd, verbosity, output_directory)
                        else:
                            # Try looking for the file in subdirectories
                            for root, _, files in os.walk(ar):
                                for potential_file in files:
                                    if potential_file.endswith('.jsonl') or potential_file.endswith('.json'):
                                        potential_path = os.path.join(root, potential_file)
                                        if os.path.exists(potential_path):
                                            print(" -> {} -> found potential MFT file: {}".format(
                                                datetime.now().isoformat().replace("T", " "),
                                                potential_file
                                            ))
                                            analyse_mft_json_func(stage, vssimage, potential_path, anysd, verbosity, output_directory)
                                            break
    except Exception as e:
        print(" -> {} -> error parsing status.log: {}".format(
            datetime.now().isoformat().replace("T", " "),
            str(e)[:100]
        ))


def analyse_artefacts(
    verbosity, output_directory, img, mnt, analysis, magicbytes, extractiocs, vssimage
):
    def analyse_mft_json(stage, vssimage, filepath, anysd, verbosity, output_directory):
        """Analyse MFT data from Artemis JSON output for EA, ADS, and Timestomping."""
        print(" -> {} -> analysing MFT for Extended Attributes, Alternate Data Streams & Timestomping...".format(
            datetime.now().isoformat().replace("T", " ")
        ))

        # Counters for findings
        ads_count = 0
        ea_count = 0
        timestomp_count = 0
        records_processed = 0

        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                # Handle both JSON array and JSONL formats
                content = f.read().strip()
                if content.startswith('['):
                    records = json.loads(content)
                else:
                    # JSONL format
                    records = []
                    for line in content.split('\n'):
                        if line.strip():
                            try:
                                records.append(json.loads(line))
                            except:
                                pass

            print(" -> {} -> processing {} MFT records...".format(
                datetime.now().isoformat().replace("T", " "),
                len(records)
            ))

            for record in records:
                records_processed += 1
                if not isinstance(record, dict):
                    continue

                filename = record.get('filename', record.get('full_path', 'unknown'))
                is_file = record.get('is_file', True)

                if not is_file:
                    continue

                # Check for Alternate Data Streams
                ads_info = record.get('ads_info', [])
                if ads_info and len(ads_info) > 0:
                    ads_count += 1
                    if not os.path.exists(anysd + "/analysis.csv"):
                        with open(anysd + "/analysis.csv", "a") as analysisfile:
                            analysisfile.write(
                                "LastWriteTime,elrond_host,Filename,AnalysisType,AnalysisValue\n"
                            )
                    with open(anysd + "/analysis.csv", "a") as analysisfile:
                        for ads in ads_info:
                            ads_name = ads.get('name', 'unknown') if isinstance(ads, dict) else str(ads)
                            analysisfile.write(
                                "{},{},{},AlternateDataStream,{}\n".format(
                                    datetime.now().isoformat(),
                                    vssimage.replace("'", ""),
                                    filename,
                                    ads_name,
                                )
                            )
                    if verbosity != "":
                        print(
                            "      Alternate Data Stream identified for '{}'".format(
                                filename.split("/")[-1] if "/" in filename else filename
                            )
                        )
                    entry, prnt = "{},{},{},alternate data stream found in '{}'\n".format(
                        datetime.now().isoformat(),
                        vssimage,
                        stage,
                        filename.split("/")[-1] if "/" in filename else filename,
                    ), " -> {} -> alternate data stream found in '{}' for {}".format(
                        datetime.now().isoformat().replace("T", " "),
                        filename.split("/")[-1] if "/" in filename else filename,
                        vssimage,
                    )
                    write_audit_log_entry(verbosity, output_directory, entry, prnt)

                # Check for Extended Attributes
                attributes = record.get('attributess', record.get('attributes', []))
                has_ea = False
                if isinstance(attributes, list):
                    for attr in attributes:
                        if isinstance(attr, dict) and attr.get('attribute_type') == 'ExtendedAttribute':
                            has_ea = True
                            break
                        elif isinstance(attr, str) and 'extended' in attr.lower():
                            has_ea = True
                            break

                if has_ea:
                    ea_count += 1
                    if not os.path.exists(anysd + "/analysis.csv"):
                        with open(anysd + "/analysis.csv", "a") as analysisfile:
                            analysisfile.write(
                                "LastWriteTime,elrond_host,Filename,AnalysisType,AnalysisValue\n"
                            )
                    with open(anysd + "/analysis.csv", "a") as analysisfile:
                        analysisfile.write(
                            "{},{},{},ExtendedAttributes,Yes\n".format(
                                datetime.now().isoformat(),
                                vssimage.replace("'", ""),
                                filename,
                            )
                        )
                    if verbosity != "":
                        print(
                            "      Extended Attributes identified for '{}'".format(
                                filename.split("/")[-1] if "/" in filename else filename
                            )
                        )
                    entry, prnt = "{},{},{},extended attribute found in '{}'\n".format(
                        datetime.now().isoformat(),
                        vssimage,
                        stage,
                        filename.split("/")[-1] if "/" in filename else filename,
                    ), " -> {} -> extended attribute found in '{}' for {}".format(
                        datetime.now().isoformat().replace("T", " "),
                        filename.split("/")[-1] if "/" in filename else filename,
                        vssimage,
                    )
                    write_audit_log_entry(verbosity, output_directory, entry, prnt)

                # Check for Timestomping ($SI vs $FN timestamp mismatch)
                # Artemis provides both standard timestamps and filename timestamps
                si_created = record.get('created', 0)
                si_modified = record.get('modified', 0)
                fn_created = record.get('filename_created', 0)
                fn_modified = record.get('filename_modified', 0)

                # Timestomping indicators:
                # 1. $SI timestamp is earlier than $FN timestamp (impossible naturally)
                # 2. Timestamps with suspicious patterns (all zeros in microseconds)
                if si_created and fn_created:
                    try:
                        si_ts = int(si_created) if isinstance(si_created, (int, float)) else 0
                        fn_ts = int(fn_created) if isinstance(fn_created, (int, float)) else 0

                        # $SI created before $FN created suggests timestomping
                        if si_ts > 0 and fn_ts > 0 and si_ts < fn_ts:
                            timestomp_count += 1
                            if not os.path.exists(anysd + "/analysis.csv"):
                                with open(anysd + "/analysis.csv", "a") as analysisfile:
                                    analysisfile.write(
                                        "LastWriteTime,elrond_host,Filename,AnalysisType,AnalysisValue\n"
                                    )
                            with open(anysd + "/analysis.csv", "a") as analysisfile:
                                analysisfile.write(
                                    "{},{},{},Timestomp,$SI: {}|$FN: {}\n".format(
                                        datetime.now().isoformat(),
                                        vssimage.replace("'", ""),
                                        filename,
                                        si_ts,
                                        fn_ts,
                                    )
                                )
                            if verbosity != "":
                                print(
                                    "      Evidence of Timestomping identified for '{}'".format(
                                        filename.split("/")[-1] if "/" in filename else filename
                                    )
                                )
                            entry, prnt = "{},{},{},evidence of timestomping found in '{}'\n".format(
                                datetime.now().isoformat(),
                                vssimage,
                                stage,
                                filename.split("/")[-1] if "/" in filename else filename,
                            ), " -> {} -> evidence of timestomping found in '{}' for {}".format(
                                datetime.now().isoformat().replace("T", " "),
                                filename.split("/")[-1] if "/" in filename else filename,
                                vssimage,
                            )
                            write_audit_log_entry(verbosity, output_directory, entry, prnt)
                    except (ValueError, TypeError):
                        pass

        except Exception as e:
            print(" -> {} -> warning: could not analyse MFT JSON: {}".format(
                datetime.now().isoformat().replace("T", " "),
                str(e)[:100]
            ))

        # Print summary
        print(" -> {} -> MFT analysis complete: {} records processed".format(
            datetime.now().isoformat().replace("T", " "),
            records_processed
        ))
        print(" -> {} ->   Extended Attributes: {} files".format(
            datetime.now().isoformat().replace("T", " "),
            ea_count
        ))
        print(" -> {} ->   Alternate Data Streams: {} files".format(
            datetime.now().isoformat().replace("T", " "),
            ads_count
        ))
        print(" -> {} ->   Timestomping indicators: {} files".format(
            datetime.now().isoformat().replace("T", " "),
            timestomp_count
        ))

    def analyse_disk_images(stage, vssimage, ar, f, anysd):
        print()
        print(
            "     Analysing MFT for Extended Attributes, Alternate Data Streams & Timestomping for {}...".format(
                vssimage
            )
        )
        with open(ar + "/" + f) as afh:
            for line in afh:
                mftinfo = re.findall(
                    r"[^\,]*\,[^\,]*\,[^\,]*\,([^\,]*)\,[^\,]*\,[^\,]*\,[^\,]*\,([^\,]*)\,([^\,]*)\,[^\,]*\,[^\,]*\,[^\,]*\,([^\,]*)\,[^\,]*\,[^\,]*\,[^\,]*\,[^\,]*\,[^\,]*\,[^\,]*\,[^\,]*\,[^\,]*\,[^\,]*\,[^\,]*\,[^\,]*\,[^\,]*\,[^\,]*\,[^\,]*\,[^\,]*\,[^\,]*\,[^\,]*\,[^\,]*\,[^\,]*\,[^\,]*\,[^\,]*\,[^\,]*\,[^\,]*\,[^\,]*\,[^\,]*\,[^\,]*\,[^\,]*\,[^\,]*\,[^\,]*\,[^\,]*\,[^\,]*\,[^\,]*\,[^\,]*\,([^\,]*)\,([^\,]*)\,[^\,]*\,[^\,]*\,[^\,]*\,[^\,]*\,[^\,]*\,([^\,]*)\,[^\,]*\,[^\,]*\,[^\,]*",
                    line,
                )
                if len(mftinfo) > 0 and (
                    (
                        mftinfo[0][0] == "File"
                        and mftinfo[0][1] != "NoFNRecord"
                        and (
                            mftinfo[0][4] == "True"
                            or mftinfo[0][5] == "True"
                            or mftinfo[0][6] == "Y"
                        )
                    )
                    or (
                        mftinfo[0][0] == "file"
                        and mftinfo[0][1] != "nofnrecord"
                        and (
                            mftinfo[0][4] == "true"
                            or mftinfo[0][5] == "true"
                            or mftinfo[0][6] == "y"
                        )
                    )
                ):
                    if not os.path.exists(anysd + "/analysis.csv"):
                        with open(anysd + "/analysis.csv", "a") as analysisfile:
                            analysisfile.write(
                                "LastWriteTime,elrond_host,Filename,AnalysisType,AnalysisValue\n"
                            )
                    else:
                        with open(anysd + "/analysis.csv", "a") as analysisfile:
                            if (mftinfo[0][4] == "True" or mftinfo[0][5] == "True") or (
                                mftinfo[0][4] == "true" or mftinfo[0][5] == "true"
                            ):
                                analysisfile.write(
                                    "{},{},{},ExtendedAttributes,Yes\n".format(
                                        datetime.now().isoformat(),
                                        vssimage.replace("'", ""),
                                        mftinfo[0][1],
                                    )
                                )
                                if verbosity != "":
                                    print(
                                        "      Extended Attributes identified for '{}'".format(
                                            mftinfo[0][1].split("/")[-1]
                                        )
                                    )
                                (
                                    entry,
                                    prnt,
                                ) = "{},{},{},extended attribute found in '{}'\n".format(
                                    datetime.now().isoformat(),
                                    vssimage,
                                    stage,
                                    mftinfo[0][1].split("/")[-1],
                                ), " -> {} -> extended attribute found in '{}' for {}".format(
                                    datetime.now().isoformat().replace("T", " "),
                                    mftinfo[0][1].split("/")[-1],
                                    vssimage,
                                )
                                write_audit_log_entry(
                                    verbosity, output_directory, entry, prnt
                                )
                            elif mftinfo[0][6] == "Y" or mftinfo[0][6] == "y":
                                analysisfile.write(
                                    "{},{},{},AlternateDataStream,Yes\n".format(
                                        datetime.now().isoformat(),
                                        vssimage.replace("'", ""),
                                        mftinfo[0][1],
                                    )
                                )
                                if verbosity != "":
                                    print(
                                        "      Alternate Data Stream identified for '{}'".format(
                                            mftinfo[0][1].split("/")[-1]
                                        )
                                    )
                                (
                                    entry,
                                    prnt,
                                ) = "{},{},{},alternate data stream found in '{}'\n".format(
                                    datetime.now().isoformat(),
                                    vssimage,
                                    stage,
                                    mftinfo[0][1].split("/")[-1],
                                ), " -> {} -> alternate data stream found in '{}' for {}".format(
                                    datetime.now().isoformat().replace("T", " "),
                                    mftinfo[0][1].split("/")[-1],
                                    vssimage,
                                )
                                write_audit_log_entry(
                                    verbosity, output_directory, entry, prnt
                                )
                            if (
                                mftinfo[0][2].split(".")[0]
                                != mftinfo[0][3].split(".")[0]
                            ):
                                stdepoch, fnepoch = int(
                                    time.mktime(
                                        time.strptime(
                                            mftinfo[0][2].split(".")[0],
                                            strpformat,
                                        )
                                    )
                                ), int(
                                    time.mktime(
                                        time.strptime(
                                            mftinfo[0][3].split(".")[0],
                                            strpformat,
                                        )
                                    )
                                )
                                if (
                                    stdepoch < fnepoch
                                    or mftinfo[0][2][20:] == "000000"
                                    or mftinfo[0][3][20:] == "000000"
                                ):
                                    with open(
                                        anysd + "/analysis.csv", "a"
                                    ) as analysisfile:
                                        analysisfile.write(
                                            "{},{},{},Timestomp,$SI: {}|$FN: {}\n".format(
                                                datetime.now().isoformat(),
                                                vssimage.replace("'", ""),
                                                mftinfo[0][1],
                                                stdepoch,
                                                fnepoch,
                                            )
                                        )
                                    if verbosity != "":
                                        print(
                                            "      Evidence of Timestomping identified for '{}'".format(
                                                mftinfo[0][1].split("/")[-1]
                                            )
                                        )
                                    (
                                        entry,
                                        prnt,
                                    ) = "{},{},{},evidence of timestomping found in '{}'\n".format(
                                        datetime.now().isoformat(),
                                        vssimage,
                                        stage,
                                        mftinfo[0][1].split("/")[-1],
                                    ), " -> {} -> evidence of timestomping found in '{}' for {}".format(
                                        datetime.now().isoformat().replace("T", " "),
                                        mftinfo[0][1].split("/")[-1],
                                        vssimage,
                                    )
                                    write_audit_log_entry(
                                        verbosity, output_directory, entry, prnt
                                    )
        print(
            "     Completed analysis of Extended Attributes, Alternate Data Streams & Timestomping for {}...".format(
                vssimage
            )
        )
        print()

    stage = "analysing"
    atftd = output_directory + img.split("::")[0] + "/artefacts/cooked/"
    anysd = output_directory + img.split("::")[0] + "/analysis/"
    strpformat = "%Y-%m-%d %H:%M:%S"
    if analysis:
        if "vss" in img.split("::")[1]:
            atftd, vssimage = (
                output_directory
                + img.split("::")[0]
                + "/artefacts/cooked/"
                + img.split("::")[1].split("_")[1],
                "'"
                + img.split("::")[0]
                + "' ("
                + img.split("::")[1]
                .split("_")[1]
                .replace("vss", "volume shadow copy #")
                + ")",
            )
        else:
            atftd, vssimage = (
                output_directory + img.split("::")[0] + "/artefacts/cooked/",
                "'" + img.split("::")[0] + "'",
            )
        print("    Analsying artefacts for {}...".format(vssimage))
        entry, prnt = "{},{},{},commenced\n".format(
            datetime.now().isoformat(), vssimage.replace("'", ""), stage
        ), " -> {} -> {} artefacts for {}".format(
            datetime.now().isoformat().replace("T", " "), stage, vssimage
        )
        write_audit_log_entry(verbosity, output_directory, entry, prnt)
        if not os.path.exists(anysd):
            os.mkdir(anysd)
        with open(anysd + "/analysis.csv", "a") as analysisfile:
            analysisfile.write(
                "LastWriteTime,hostname,Filename,analysis_type,analysis_value\n"
            )
        if magicbytes:
            print(
                "     Analysing files for file-signature (magic-byte) discrepencies for {}...".format(
                    vssimage
                )
            )
            for root, _, files in os.walk(mnt):
                for f in files:
                    try:
                        if (
                            os.stat(os.path.join(root, f)).st_size > 0
                            and os.stat(os.path.join(root, f)).st_size < 10000000
                        ):  # 10MB
                            if (
                                os.path.join(root, f) != "/mnt/elrond_mount/hiberfil.sys"
                                and os.path.join(root, f)
                                != "/mnt/elrond_mount/pagefile.sys"
                                and os.path.join(root, f)
                                != "/mnt/elrond_mount1/hiberfil.sys"
                                and os.path.join(root, f)
                                != "/mnt/elrond_mount1/pagefile.sys"
                                and os.path.join(root, f)
                                != "/mnt/elrond_mount2/hiberfil.sys"
                                and os.path.join(root, f)
                                != "/mnt/elrond_mount2/pagefile.sys"
                                and os.path.join(root, f)
                                != "/mnt/elrond_mount3/hiberfil.sys"
                                and os.path.join(root, f)
                                != "/mnt/elrond_mount3/pagefile.sys"
                                and os.path.join(root, f)
                                != "/mnt/elrond_mount4/hiberfil.sys"
                                and os.path.join(root, f)
                                != "/mnt/elrond_mount4/pagefile.sys"
                                and os.path.join(root, f)
                                != "/mnt/elrond_mount5/hiberfil.sys"
                                and os.path.join(root, f)
                                != "/mnt/elrond_mount5/pagefile.sys"
                            ) and (
                                "." in f
                                and (
                                    f.endswith(".cab")
                                    or f.endswith(".elf")
                                    or f.endswith(".doc")
                                    or f.endswith(".xls")
                                    or f.endswith(".ppt")
                                    or f.endswith(".pdf")
                                    or f.endswith(".odt")
                                    or f.endswith(".odp")
                                    or f.endswith(".ott")
                                    or f.endswith(".zip")
                                    or f.endswith(".rar")
                                    or f.endswith(".7z")
                                    or f.endswith(".chm")
                                    or f.endswith(".docx")
                                    or f.endswith(".xlsx")
                                    or f.endswith(".pptx")
                                    or f.endswith(".com")
                                    or f.endswith(".dll")
                                    or f.endswith(".exe")
                                    or f.endswith(".sys")
                                    or f.endswith(".gif")
                                    or f.endswith(".jpg")
                                    or f.endswith(".jpeg")
                                    or f.endswith(".png")
                                )
                            ):
                                try:
                                    with open(os.path.join(root, f), "rb") as magic_file:
                                        file_hdr = magic_file.read()
                                except:
                                    file_hdr = "0000000000"
                                if (
                                    file_hdr != "0000000000"
                                    and str(file_hdr)[2:10] != "'"
                                    and (
                                        (
                                            f.endswith(".cab")
                                            and str(file_hdr)[2:10] != "\\x4d\\x53"
                                            and str(file_hdr)[2:10] != "MSCF\\x00"
                                        )
                                        or (
                                            f.endswith(".elf")
                                            and str(file_hdr)[2:10] != "\\x7f\\x45"
                                            and str(file_hdr)[2:10] != "\\x7fELF\\"
                                        )
                                        or (
                                            (
                                                f.endswith(".com")
                                                or f.endswith(".dll")
                                                or f.endswith(".exe")
                                                or f.endswith(".sys")
                                            )
                                            and (
                                                str(file_hdr)[2:10] != "\\x4d\\x5a"
                                                and str(file_hdr)[2:10] != "MZ\\x90\\x"
                                                and str(file_hdr)[2:10] != "MZ\\x00\\x"
                                                and str(file_hdr)[2:10] != "MZx\\x00\\"
                                                and str(file_hdr)[2:10] != "MZ\\x9f\\x"
                                                and str(file_hdr)[2:10] != "\\x00\\x02"
                                                and str(file_hdr)[2:10] != "\\x02\\x00"
                                                and str(file_hdr)[2:9] != "DCH\\x01"
                                                and str(file_hdr)[2:9] != "DCD\\x01"
                                                and str(file_hdr)[2:9] != "DCN\\x01"
                                                and str(file_hdr)[2:9] != "DCN\\x01"
                                            )
                                        )
                                        or (
                                            (
                                                f.endswith(".docx")
                                                or f.endswith(".xlsx")
                                                or f.endswith(".pptx")
                                            )
                                            and str(file_hdr)[2:10] != "\\x50\\x4b"
                                            and str(file_hdr)[2:10] != "PK\\x03\\x"
                                        )
                                        or (
                                            (
                                                f.endswith(".doc")
                                                or f.endswith(".xls")
                                                or f.endswith(".ppt")
                                            )
                                            and (str(file_hdr)[2:10] != "\\x50\\x4b")
                                            and str(file_hdr)[2:10] != "\\xd0\\xcf"
                                        )
                                        or (
                                            (
                                                f.endswith(".odt")
                                                or f.endswith(".odp")
                                                or f.endswith(".ott")
                                            )
                                            and str(file_hdr)[2:10] != "\\x50\\x4b"
                                            and str(file_hdr)[2:10] != "PK\\x03\\x"
                                        )
                                        or (
                                            f.endswith(".pdf")
                                            and (
                                                str(file_hdr)[2:9] != "%PDF-1."
                                                and str(file_hdr)[2:10] != "\\x25\\x50"
                                            )
                                        )
                                        or (
                                            f.endswith(".7z")
                                            and (
                                                str(file_hdr)[2:10] != "7z\\xbc\\x"
                                                and str(file_hdr)[2:10] != "\\x37\\x7a"
                                            )
                                        )
                                        or (
                                            (f.endswith(".jar") or f.endswith(".zip"))
                                            and str(file_hdr)[2:10] != "\\x50\\x4b"
                                            and str(file_hdr)[2:10] != "PK\\x03\\x"
                                            and str(file_hdr)[2:9] != "PK\\x03"
                                        )
                                        or (
                                            f.endswith(".rar")
                                            and (
                                                str(file_hdr)[2:10] != "Rar!\\x1a"
                                                and str(file_hdr)[2:10] != "\\x52\\x61"
                                            )
                                        )
                                        or (
                                            (f.endswith(".jpg") or f.endswith(".jpeg"))
                                            and (str(file_hdr)[2:10] != "\\xff\\xd8")
                                            and str(file_hdr)[2:10] != "GIF89a\\x"
                                            and str(file_hdr)[2:9] != "DCH\\x01"
                                        )
                                        or (
                                            f.endswith(".gif")
                                            and (
                                                str(file_hdr)[2:8] != "GIF89a"
                                                and str(file_hdr)[2:8] != "GIF87a"
                                                and str(file_hdr)[2:10] != "\\x47\\x49"
                                            )
                                        )
                                        or (
                                            f.endswith(".png")
                                            and (
                                                str(file_hdr)[2:10] != "\\x89\\x50"
                                                and str(file_hdr)[2:10] != "\\x89PNG\\"
                                                and str(file_hdr)[2:10] != "\\xff\\xd8"
                                            )
                                        )
                                        or (
                                            f.endswith(".chm")
                                            and (
                                                str(file_hdr)[2:10] != "ITSF\\x03"
                                                and str(file_hdr)[2:10] != "\\x49\\x54"
                                            )
                                        )
                                    )
                                ):
                                    with open(anysd + "/analysis.csv", "a") as analysisfile:
                                        analysisfile.write(
                                            "{},{},{},File-signature (magic-byte) Discrepency,'{}'\n".format(
                                                datetime.now().isoformat(),
                                                vssimage.replace("'", ""),
                                                f,
                                                str(file_hdr)[2:10],
                                            )
                                        )
                                    if verbosity != "":
                                        print(
                                            "      File-signature (magic-byte) discrepency of '{}' identified for {}".format(
                                                str(file_hdr)[2:10],
                                                f.split("/")[-1],
                                            )
                                        )
                                    (
                                        entry,
                                        prnt,
                                    ) = "{},{},{},file-signature (magic-byte) discrepency of '{}' for '{}'\n".format(
                                        datetime.now().isoformat(),
                                        vssimage,
                                        stage,
                                        str(file_hdr)[2:10],
                                        f,
                                    ), " -> {} -> identified file-signature (magic-byte) discrepency of '{}' from '{}' for {}".format(
                                        datetime.now().isoformat().replace("T", " "),
                                        str(file_hdr)[2:10],
                                        f,
                                        vssimage,
                                    )
                                    write_audit_log_entry(
                                        verbosity, output_directory, entry, prnt
                                    )
                    except:
                        pass
        # Analyze MFT data for Extended Attributes, Alternate Data Streams, and Timestomping
        print(" -> {} -> scanning for MFT data to analyse for '{}'...".format(
            datetime.now().isoformat().replace("T", " "), img.split("::")[0]
        ))
        mft_files_found = False
        for ar, _, af in os.walk(atftd):
            for f in af:
                # Handle both legacy CSV format and new Artemis JSON format
                img_parts = img.split("::")
                img_mount = img_parts[1] if len(img_parts) > 1 else ""

                # Check if this is a VSS path or regular cooked directory
                is_vss_path = "vss" in img_mount.lower()
                is_cooked_dir = "cooked" in ar.lower()

                if is_vss_path:
                    vss_part = img_mount.split("_")[1] if "_" in img_mount else ""
                    if vss_part in atftd:
                        if f.endswith("MFT.csv"):
                            mft_files_found = True
                            analyse_disk_images(stage, vssimage, ar, f, anysd)
                        elif f.lower() in ("mft.json", "mft.jsonl", "rawfiles.json", "rawfiles.jsonl"):
                            mft_files_found = True
                            analyse_mft_json(stage, vssimage, os.path.join(ar, f), anysd, verbosity, output_directory)
                        # Handle Artemis UUID-named output files
                        elif f == "status.log":
                            mft_files_found = True
                            _analyse_artemis_mft_from_status_log(ar, f, stage, vssimage, anysd, verbosity, output_directory, analyse_mft_json)
                elif is_cooked_dir:
                    if f.endswith("MFT.csv"):
                        mft_files_found = True
                        analyse_disk_images(stage, vssimage, ar, f, anysd)
                    elif f.lower() in ("mft.json", "mft.jsonl", "rawfiles.json", "rawfiles.jsonl"):
                        mft_files_found = True
                        analyse_mft_json(stage, vssimage, os.path.join(ar, f), anysd, verbosity, output_directory)
                    # Handle Artemis UUID-named output files via status.log
                    elif f == "status.log":
                        mft_files_found = True
                        _analyse_artemis_mft_from_status_log(ar, f, stage, vssimage, anysd, verbosity, output_directory, analyse_mft_json)
                    # Also scan any JSONL files that might be Artemis MFT output (UUID-named)
                    elif f.endswith(".jsonl") and len(f) > 30:  # UUID-named files are typically 36+ chars
                        # Check if this looks like an MFT output by sampling content
                        try:
                            filepath = os.path.join(ar, f)
                            with open(filepath, 'r', encoding='utf-8', errors='replace') as sample_file:
                                first_line = sample_file.readline()
                                if first_line:
                                    sample_data = json.loads(first_line)
                                    # Check for MFT-related fields
                                    if any(key in sample_data for key in ['filename', 'full_path', 'created', 'modified', 'ads_info', 'attributes']):
                                        print(" -> {} -> found potential MFT data in '{}'".format(
                                            datetime.now().isoformat().replace("T", " "), f
                                        ))
                                        mft_files_found = True
                                        analyse_mft_json(stage, vssimage, filepath, anysd, verbosity, output_directory)
                        except:
                            pass

        if not mft_files_found:
            print(" -> {} -> no Extended Attributes found for '{}'".format(
                datetime.now().isoformat().replace("T", " "), img.split("::")[0]
            ))
            print(" -> {} -> no Alternate Data Streams found for '{}'".format(
                datetime.now().isoformat().replace("T", " "), img.split("::")[0]
            ))
            print(" -> {} -> no evidence of Timestomping found for '{}'".format(
                datetime.now().isoformat().replace("T", " "), img.split("::")[0]
            ))
    if extractiocs:
        iocfilelist, lineno, previous = [], 0, 0.0
        if verbosity != "":
            print(
                "\n    \033[1;33mUndertaking IOC extraction for '{}'...\033[1;m".format(
                    img.split("::")[0]
                )
            )
        print(
            "     Assessing readable files to extract IOCs from, for '{}'...".format(
                img.split("::")[0]
            )
        )
        for root, _, files in os.walk(mnt):
            for f in files:
                try:
                    if (
                        os.stat(os.path.join(root, f)).st_size > 0
                        and os.stat(os.path.join(root, f)).st_size < 10000000
                    ):  # 10MB
                        with open(os.path.join(root, f), "r") as filetest:
                            filetest.readline()
                            iocfilelist.append(os.path.join(root, f))
                except:
                    pass
        if os.path.exists(
            os.path.join(output_directory, img.split("::")[0], "artefacts")
        ):
            for root, _, files in os.walk(
                os.path.join(output_directory, img.split("::")[0], "artefacts")
            ):
                for f in files:
                    try:
                        if (
                            os.stat(os.path.join(root, f)).st_size > 0
                            and os.stat(os.path.join(root, f)).st_size < 10000000
                        ):  # 10MB
                            with open(os.path.join(root, f), "r") as filetest:
                                filetest.readline()
                                iocfilelist.append(os.path.join(root, f))
                    except:
                        pass
        print("       Done.")
        iocfiles = list(set(iocfilelist))
        if not os.path.exists(anysd):
            os.mkdir(anysd)
        if not os.path.exists(
            output_directory + img.split("::")[0] + "/analysis/iocs.csv"
        ):
            with open(
                output_directory + img.split("::")[0] + "/analysis/iocs.csv",
                "w",
            ) as ioccsv:
                ioccsv.write(
                    "CreationTime,LastAccessTime,LastWriteTime,Filename,ioc,indicator_type,line_number,resolvable\n"
                )
        compare_iocs(
            output_directory,
            verbosity,
            img,
            stage,
            vssimage,
            iocfiles,
            lineno,
            previous,
        )
    entry, prnt = "{},{},{},completed\n".format(
        datetime.now().isoformat(), vssimage, stage
    ), " -> {} -> analysis completed for {}".format(
        datetime.now().isoformat().replace("T", " "), vssimage
    )
    write_audit_log_entry(verbosity, output_directory, entry, prnt)
    print(" -> Completed Analysis Phase for {}".format(vssimage))
    print()
