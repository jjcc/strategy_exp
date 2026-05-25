import time
import pandas as pd
import requests
import os
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
load_dotenv()

token = os.getenv("TOKEN")
query_id = os.getenv("QUERY_ID")
flex_version = 3

requestBase = "https://ndcdyn.interactivebrokers.com/AccountManagement/FlexWebService"


def send_flex_query(token, query_id, flex_version, requestBase):
    send_slug= "/SendRequest"
    send_params = {
    "t":token, 
    "q":query_id, 
    "v":flex_version
    }

    flexReq = requests.get(url=requestBase+send_slug, params=send_params)
    if flexReq.status_code == 200:
        print("Request sent successfully.")
        print(flexReq.text)
        return flexReq.text
    else:
        return None

# send_flex_query(token, queryId, flex_version, requestBase)
def receive_flex_query_result(token, refCode, flex_version, requestBase):
    receive_slug = "/GetStatement"
    receive_params = {
        "t":token, 
        "q":refCode, 
        "v":flex_version
    }
    receiveUrl = requests.get(url=requestBase + receive_slug, params=receive_params, allow_redirects=True)
    return receiveUrl.content

def parse_flex_query_result(resp_content: str):
    """
    Parse the content of the flex query result, which is expected to be in CSV format with multiple segments.
    Each segment starts with a line that begins with "ClientAccountID". The function separates the content into segments and returns a list of segments, where each segment is a list of lines.
    """
    file_content =  resp_content
    # Process the data as needed
    lines = file_content.splitlines()
    # separate the contenet by lines started with "ClientAccountID"
    segs = []
    new_seg = []
    for line in lines:
        if line.startswith("\"ClientAccountID"):
            # Process each line as needed
            if len(new_seg) > 0:
                segs.append(new_seg)
            new_seg = []
            continue
        new_seg.append(line)
    if len(new_seg) > 0:
        segs.append(new_seg)
    return segs

def parse_request(query_response: str):
    """
    Parse the response from sending a flex query to extract the ReferenceCode, which is needed to retrieve the results later.
    The response is expected to be in XML format, and the function uses xml.etree.ElementTree to parse it.
    """
    tree = ET.ElementTree(ET.fromstring(query_response))
    root = tree.getroot()
    resp_ref_code = None
    for child in root:
        print(child.tag, child.text)
        if child.tag == "ReferenceCode":
            resp_ref_code = child.text
    return resp_ref_code

def convert_seg2_to_df(seg_content: list):
    """
    Convert the content of the second segment (which contains the trade data) into a pandas DataFrame. The first line of the segment is expected to contain the column names, and the subsequent lines contain the data.
    """
    col_names = "ClientAccountID","UnderlyingSymbol","Strike","Expiry","Put/Call","ReportDate","Quantity","CostBasisPrice","CostBasisMoney"
    df = pd.DataFrame([line.split(",") for line in seg_content], columns=col_names)

    for idx, line in enumerate(seg_content):
        row = line.split(",")
        if len(row) != len(col_names):
            print(f"Warning: Line has {len(row)} columns, expected {len(col_names)}. Line content: {line}")
            continue
        row =  [item.strip('"') for item in row]  # Remove surrounding quotes
        df.loc[idx] = row
    return df

if __name__ == "__main__":
    date_string = time.strftime("%Y%m%d_%H%M%S")
    resp =  send_flex_query(token, query_id, flex_version, requestBase)
    if resp is None:
        print("Failed to send flex query.")
        exit(1)

    response_example = """
<FlexStatementResponse timestamp='24 May, 2026 04:56 PM EDT'>
<Status>Success</Status>
<ReferenceCode>6302975313</ReferenceCode>
<Url>https://gdcdyn.interactivebrokers.com/AccountManagement/FlexWebService/GetStatement</Url>
</FlexStatementResponse>
    """
    #refCode = parse_request(response_example)
    refCode = parse_request(resp)
    if refCode is None:
        print("Failed to parse reference code from response.")
        exit(1)
    print("Hold for Request.")
    time.sleep(20)
    #refCode = 6302975313 # it was from result of send_flex_query, can also be obtained from the URL after sending request in browser
    content = receive_flex_query_result(token, refCode, flex_version, requestBase)
    #outputPath = "output/ib_flexquery_result.csv"
    #open(outputPath, 'wb').write(content)
    data = parse_flex_query_result(content.decode('utf-8'))
    seg2 = data[1]

    # column names:
    df = convert_seg2_to_df(seg2)
    file_name = f"output/ib_flexquery_result_{refCode}_{date_string}.csv"
    df.to_csv(file_name, index=False)

    print(df)
