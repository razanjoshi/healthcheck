import json

with open('service-account.json', 'r') as f:
    data = json.load(f)

print('SPREADSHEET_ID = "your-spreadsheet-id-here"\n')
print('[service_account_info]')
for key, value in data.items():
    if key == 'private_key':
        print(f'{key} = """{value}"""')
    elif isinstance(value, str):
        print(f'{key} = "{value}"')
    else:
        print(f'{key} = {value}')