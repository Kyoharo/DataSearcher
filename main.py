
import re
from datetime import datetime, timedelta
import os
import shutil

class DataSearcher:
    def __init__(self):
        pass

    def search_data_in_file(self, file_path, target_ticket):
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    if target_ticket in line:
                        match = re.match(r'^\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*[^|]+\s*\|\s*[^|]+\s*\|\s*([^|]+)\s*\|', line)
                        if match:
                            username = match.group(1).strip()
                            hash_value = match.group(2).strip()
                            date_str = match.group(3).strip()

                            # Convert date to desired format
                            date = datetime.strptime(date_str, "%m/%d/%y")
                            date += timedelta(days=6*30)  # Add 6 months (assuming 30 days per month)
                            formatted_date = date.strftime("%b %d %Y")
                            return username, hash_value, formatted_date
                return None
        except FileNotFoundError:
            print("File not found.")
            return None
        except Exception as e:
            print("An error occurred:", e)
            return None
        


    def update_data_in_files(self, files_to_edit, target_username, new_hash, new_date):
        for file_path in files_to_edit:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as file:
                        content = file.read()
                    user_pattern = re.compile(r'user = ' + re.escape(target_username) + r' {(.*?)\}', re.DOTALL)
                    match = user_pattern.search(content)
                    if match:
                        user_block = match.group(1)
                        user_block = re.sub(r'login = .*', f'login = {new_hash}', user_block)
                        user_block = re.sub(r'expires = ".*?"', f'expires = "{new_date}"', user_block, count=1)
                        updated_content = content[:match.start(1)] + user_block + content[match.end(1):]

                        # Write the updated content back to the file
                        with open(file_path, 'w') as file:
                            file.write(updated_content)
                        print(f"Hash and expiration date updated successfully in file {file_path}")
                    else:
                        print(f"User not found in file {file_path}")
                except Exception as e:
                    print("An error occurred:", e)
                    return None

    def backup_folder(self, folder_path, backup_location):
        try:
            folder_name = os.path.basename(folder_path)
            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

            backup_folder_name = f"{folder_name}_{timestamp}"
            backup_folder_path = os.path.join(backup_location, backup_folder_name)

            shutil.copytree(folder_path, backup_folder_path)
            print(f"Backup of {folder_path} created successfully at {backup_folder_path}")
        except Exception as e:
            print(f"Error occurred while creating backup: {e}")

                



file_to_edit = ["/etc/tac_plus/tac_plus.conf",     
                "/etc/tac_plus/tac_plus-ASR-Read.conf",
                "/etc/tac_plus/tac_plus-ASR.conf",
                "/etc/tac_plus/tac_plus-core.conf", 
                "/etc/tac_plus/tac_plus-DC.conf",
                "/etc/tac_plus/tac_plus-BRAS.conf",   
                "/etc/tac_plus/tac_plus-Access-SWs.conf",   
                "/etc/tac_plus/tac_plus-Wifi.conf"
]
searcher = DataSearcher()
searcher.backup_folder("/etc/tac_plus/","/home/kyoharo/Desktop/Projects/tal3at")
ticket_number = input("Enter your ticket number: ")
result = searcher.search_data_in_file("/var/log/hash", ticket_number)
print(result)
if result != None:
    target_username = result[0]
    new_hash = result[1]
    new_hash = f'des {new_hash}'
    new_date = result[2]
    searcher.update_data_in_files(file_to_edit, target_username, new_hash, new_date)
