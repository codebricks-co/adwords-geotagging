# aj-hung-ads-api

Work on Ads API for AJ Hung.

Add tokens to the googleads.yaml file following the instructions in the below link:
https://developers.google.com/adwords/api/docs/guides/first-api-call

There are two major operations
1. Output the pincodes of current campaigns to a file.
2. Update the pincodes of campaigns from a file.

In the src folder, create folders as:
```
files/input
files/output
```

Store CSV files in these as per your requirement. The format of the CSV is
```
campaignId1,zipCode1,zipCode2,...
campaignId2,zipCodeX,zipCodeY...
```

You can now run the code with 
```
cd src
python main.py
```
