import csv
from collections import defaultdict

HEADER_ALIASES = {
    "TC_ID": ["TC_ID/PC_ID", "TC_ID", "PC_ID"],
    "DESCRIPTION": ["Testcase_Description", "Description", "Test Description"],
    "SERVICE": ["Service_ID", "SID", "Service"],
    "SUBFUNC": ["SubService_ID", "SubFunction", "DID"],
    "EXPECTED": ["Expected_Response_Data", "Expected", "Response"],
    "WRITE": ["Write_Data", "Data", "Payload"],
    "ADDRESSING": ["Addressing", "Mode"],
    "FORMAT": ["Format"],
    "STATUS_MASK": ["Status_Mask", "StatusMask"],
    "COMM_TYPE": ["Communication_Type", "CommunicationType"],
    "CONTROLTYPE": ["controltype", "ControlType"],
}
def find_column(col, aliases):
    for alias in aliases:
        if alias in col:
            return col[alias]
    raise KeyError(f"Column not found. Tried: {aliases}")

grouped_cases = defaultdict(list)


def load_testcases(file_path):
    grouped_cases.clear()
    try:
        with open(file_path, "r") as f:
            reader = csv.reader(f)
            header = [h.strip().lstrip("#") for h in next(reader)]
            col = {
                name : idx
                for idx, name in enumerate(header)
            }
            
            current_tc_id = None
            for row in reader:
                if not row:
                    continue  # Skip empty or malformed lines
                row_values = [str(cell).strip().upper() for cell in row]
                cmd = None
                if "WAIT" in row_values:
                    cmd = "WAIT"
                elif "AWAIT_VALUE_MATCH" in row_values:
                    cmd = "AWAIT_VALUE_MATCH"
                        
                if cmd == "WAIT":
                    if current_tc_id:
                        wait_index = row_values.index("WAIT")
                        wait_value = row[wait_index + 1].strip()
                        grouped_cases[current_tc_id].append(
                            (
                                "WAIT",
                                int(wait_value, 16)
                            )
                        )
                    continue    
                if cmd == "AWAIT_VALUE_MATCH":
                    if current_tc_id:
                        await_index = row_values.index("AWAIT_VALUE_MATCH")
                        expected_value = row[await_index + 1].strip()
                        timeout_value = int(row[await_index + 2].strip(), 16)
                        grouped_cases[current_tc_id].append(
                            (
                                "AWAIT_VALUE_MATCH",
                                expected_value,
                                timeout_value
                            )
                        )
                    continue
                if len(row) < 5:
                    continue

                tc_id = row[find_column(col, HEADER_ALIASES["TC_ID"])].strip()
                current_tc_id = tc_id
                step_desc = row[find_column(col, HEADER_ALIASES["DESCRIPTION"])].strip()
                service_id = row[find_column(col, HEADER_ALIASES["SERVICE"])].strip()
                subfunction_or_did = row[find_column(col, HEADER_ALIASES["SUBFUNC"])].strip()
                expected_response = row[find_column(col, HEADER_ALIASES["EXPECTED"])].strip()
                write_data = row[find_column(col, HEADER_ALIASES["WRITE"])].strip()
                addressing = row[find_column(col, HEADER_ALIASES["ADDRESSING"])].strip().lower()
                format_type = row[find_column(col, HEADER_ALIASES["FORMAT"])].strip()
                status_mask = row[find_column(col, HEADER_ALIASES["STATUS_MASK"])].strip()
                communication_type = row[find_column(col, HEADER_ALIASES["COMM_TYPE"])].strip()
                controltype = row[find_column(col, HEADER_ALIASES["CONTROLTYPE"])].strip()

                grouped_cases[tc_id].append(
                    (
                        tc_id,
                        step_desc,
                        service_id,
                        subfunction_or_did,
                        expected_response,
                        write_data,
                        addressing,
                        format_type,
                        status_mask,
                        communication_type,
                        controltype,
                    )
                )

        return grouped_cases

    except Exception as e:
        print(f"Error parsing testcases: {e}")
        return {}
