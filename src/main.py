from googleads import adwords
import os
import csv
import locale
import math

PAGE_SIZE = 100
API_CALL_LIMIT = 25
COUNTRY_CODES = ['IN', 'US']
COUNTRY_NAMES = ["India"]


def read_pin_codes(client, filename):
    print("Started...")
    output = {}
    campaign_service = client.GetService(
        'CampaignCriterionService', version='v201809')
    # offset = 0
    selector = {
        'fields': ['LocationName'],
        # 'paging': {
        #     'startIndex': str(offset),
        #     'numberResults': str(PAGE_SIZE)
        # }
        'predicates': {
            'field': "CriteriaType",
            'operator': "EQUALS",
            'values': "LOCATION",
        },
    }

    # GET locations for ads
    page = campaign_service.get(selector)
    print(page)

    for entry in page['entries']:
        try:
            output[entry['campaignId']].append(
                int(entry['criterion']['locationName']))
        except:
            output[entry['campaignId']] = []
            output[entry['campaignId']].append(
                int(entry['criterion']['locationName']))

    # write locations to file
    print("Writing To file...")
    with open('files/output/' + filename + '.csv', 'w') as csv_file:
        file_output = []
        writer = csv.writer(csv_file)
        for key, value in output.items():
            temp = []
            temp.append(key)
            for code in value:
                temp.append(code)
            file_output.append(temp)

        writer.writerows(file_output)

    print("Done!")


def update_pin_codes(client, campaignId, pinCodes):
    print("\n\n Started Program \n\n")
    campaign_criterion_service = client.GetService(
        'CampaignCriterionService', version='v201809')
    location_criterion_service = client.GetService(
        "LocationCriterionService", version="v201809")

    #  REMOVE EXISTING CODES
    operations = []
    selector = {
        'fields': ['LocationName'],
        # 'paging': {
        #     'startIndex': str(offset),
        #     'numberResults': str(PAGE_SIZE)
        # }
        'predicates': {
            'field': "CriteriaType",
            'operator': "EQUALS",
            'values': "LOCATION",
        },
    }

    page = campaign_criterion_service.get(selector)
    # print(page)
    print("\n\n Removing Existing Locations \n\n")
    for entry in page['entries']:
        if(entry['campaignId'] == campaignId):
            operations.append({
                'operator': 'REMOVE',
                'operand': {
                    'campaignId': campaignId,
                    'criterion': {
                        'xsi_type': 'Location',
                        'id':  entry['criterion']['id'],
                    }
                }
            })

    if len(operations) != 0:
        result = campaign_criterion_service.mutate(operations)
    # print(result)
    print("\n\n Adding New Locations \n\n")
    i = 0
    while i < math.ceil(len(pinCodes) / API_CALL_LIMIT):
        targetPinCodes = pinCodes[i*API_CALL_LIMIT: (i+1)*API_CALL_LIMIT]
        # print(targetPinCodes)

        location_search_selector = {
            'fields': ["Id", "LocationName", "DisplayType", "CanonicalName"],
            'predicates': [
                {'field': 'LocationName',
                 'operator': "IN",
                 'values': targetPinCodes,
                 }]
        }

        final_target_ids = []
        data = location_criterion_service.get(location_search_selector)
        for entry in data:
            for location in entry['location']['parentLocations']:
                if(location['locationName'] in COUNTRY_NAMES):
                    # print(entry)
                    final_target_ids.append(entry['location']['id'])

        operations = []
        # print(final_target_ids)
        for ids in final_target_ids:
            operations.append({
                'operator': 'ADD',
                'operand': {
                    'campaignId': campaignId,
                    'criterion': {
                        'xsi_type': 'Location',
                        'id': ids,
                    }
                }
            })
            # if len(operations) == 1950:
            #     result = campaign_criterion_service.mutate(operations)
            #     operations = []
        print(i*API_CALL_LIMIT + len(targetPinCodes), "zip codes added")
        i = i + 1


def main(client):
  print("Choose an option from below \n1. Output Postal Codes to a file\n2. Add the Postal Codes to Campaigns")
  response = int(input())
  if response == 1:
      print("Enter the file name:")
      name = input()
      if len(name) == 0:
          print("Error. Please Enter valid name. Exiting Program!")
          exit()

      read_pin_codes(adwords_client, name)

  elif response == 2:
      print("Enter the file name:")
      name_input = input()
      if len(name_input) == 0:
          print("Error. File name not valid. Exiting Program!")
          exit()
      campaignId = 1
      pinCodes = []
      with open('files/input/' + name_input + '.csv') as csv_file:
          csv_reader = csv.reader(csv_file, delimiter=',')
          for row in csv_reader:
              campaignId = int(row[0])
              for code in row[1:]:
                  pinCodes.append(code)

              update_pin_codes(adwords_client, campaignId, pinCodes)

  else:
      print("Invalid Input. Exiting program!")
      exit()


if __name__ == '__main__':

  CURR_PATH = os.path.dirname(os.path.realpath(__file__))
  CRED_PATH = os.path.join(CURR_PATH, "creds", "googleads.yaml")

  locale.getdefaultlocale = (lambda *args: ['en_US', 'UTF-8'])

  adwords_client = adwords.AdWordsClient.LoadFromStorage(CRED_PATH)

  main(adwords_client)