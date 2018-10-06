import sys

if sys.version_info.major < 3:
    print("Use python3 to run the script!")
    sys.exit(1)

from urllib.request import urlopen

try:
    from bs4 import BeautifulSoup
    from twilio.rest import Client
except ImportError:
    print("Please run 'pip install -r requirements.txt'")
    sys.exit(1)


TWILIO_SID = "Twilio sid"
TWILIO_AUTH = "Twilio auth"
TWILIO_NUMBER="Twilio number to receive messages from"
PAGE_URL = "https://www.iski.istanbul/web/tr-TR/ariza-kesinti"


def parse_page():
    """Open and parse page content

    :rtype: object
    :returns: parsed page as a BeautifulSoup object
    """

    page = urlopen(PAGE_URL)
    parsed_page = BeautifulSoup(page, 'lxml')

    return parsed_page


def get_interruption_info():
    """Get the water interruption info for all regions in İstanbul

    :rtype: dictionary
    :returns: water interruption info with region as key
    """

    results = {}

    parsed_page = parse_page()

    all_info = parsed_page.findAll('div', {'class': 'table-responsive'})

    all_tables = [item for table in all_info for item in table.find_all('table')]

    for table in all_tables:

        region_found = True

        for row in table.find_all('tr'):

            column_count = 0

            for column in row.find_all('td'):
                column_count += 1

                if column_count == 3: # we are interested in third column

                    if region_found:
                        region = column.text.strip().upper()
                        results[region] = []
                        region_found = False
                    else:
                        results[region.upper()].append(column.text.strip())

    return results


def construct_message(region, info):
    """Construct message to send as sms

    :type region: string
    :param region: name of region
    :type info: string
    :param info: interruption info for the region
    :rtype: string
    :returns: message to send as sms
    """

    region_seperator = "#"*len(region)
    message = "{}\n{}\n{}\n\n".format("*", region, region_seperator)
    message += "\n*******\n".join(info)

    return message

def send_sms(message, to):
    """Send sms message to given number

    :type message: string
    :param message: message to send
    :type to: string
    :param to: phone number to send message
    """

    client = Client(TWILIO_SID, TWILIO_AUTH)

    message_result = client.messages.create(body=message, from_=TWILIO_NUMBER, to=to)


def is_requested_region_in_result(query_results, region):
    """Search if requested region is in the interruption info

    :type query_results: dictionary
    :param query_results: water interruption info
    :type region: string
    :param region: name of region
    :rtype: bool
    :returns: Whether region in the results or not
    """

    return region in query_results.keys()


if __name__ == '__main__':

    if len(sys.argv) != 3:
        print("Usage: python3 water_agent.py <region> <10 digit number to receive message>")
        sys.exit(1)

    region = sys.argv[1].upper()
    to = "+90" + sys.argv[2]
    query_results = get_interruption_info()

    if is_requested_region_in_result(query_results, region):
        message = construct_message(region, query_results[region])

        try:
            send_sms(message, to)
            print("Message sent to {}".format(to))
        except:
            print("An error occurred during message sending operation!")
    else:
        print("No water interruption for the given region!")


