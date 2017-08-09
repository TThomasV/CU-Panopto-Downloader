#importing necessary libs
import os
import time
import getpass
import glob
from selenium import webdriver

print("[!] Starting script")

# Asking user for login credentials
username = input("Enter your Cardiff uni username: ")
password = getpass.getpass()
print("[+] Details accepted")

# Set current running path
currentPath = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

# Setup & launch web driver
print("[+] Launching chromedriver.exe")
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized") # Start maximized
options.add_argument("--mute-audio") # Mute audio
# Remove remember password dialog box
options.add_experimental_option('prefs', {'credentials_enable_service': False,'profile': {'password_manager_enabled': False}})
driver = webdriver.Chrome(currentPath + '\chromedriver.exe',chrome_options=options)

print("[+] Starting login process")
try:
    driver.get("https://cardiff.cloud.panopto.eu/Panopto/Pages/Sessions/List.aspx?embedded=0#maxResults=250&isSharedWithMe=true")
    driver.find_element_by_xpath('//*[@id="loginButton"]').click()
    driver.find_element_by_xpath('//*[@id="loginControl_externalLoginButton"]').click()
    driver.find_element_by_xpath('//*[@id="user_id"]').send_keys(username)
    driver.find_element_by_xpath('//*[@id="password"]').send_keys(password)
    driver.find_element_by_xpath('//*[@id="entry-login"]').click()
    # Wait for user to login
    while True:
        time.sleep(3)
        if driver.current_url == 'https://cardiff.cloud.panopto.eu/Panopto/Pages/Sessions/List.aspx?embedded=0#maxResults=250&isSharedWithMe=true':
            print("[+] Logged in as "+username.upper())
            break
except:
    # Error
    print("[+] Unable to login - Restart script and try again with correct login details")
    print("[!] Exiting the script")
    exit()

# Sleep to allow browser to load page fully (aspx)
print("[+] Waiting for page to load")
time.sleep(5)

# Find all links that lead to videos
print("[+] Begin link scrapping")
videos = driver.find_elements_by_xpath("//a[@class='detail-title']")

# Empty dict to store links and file names
links_dict={}

# Loop through video objects and and save links
for video in videos:
    if video.text != "": # Gets rid of non video links
        links_dict[video.get_attribute("href")] = video.text

# Make output directory
if not os.path.exists(currentPath+"\\raw_vids"):
    os.makedirs(currentPath+"\\raw_vids")

# Iterate through each video
for key, value in links_dict.items():
    try:
        driver.get(key) # Go to video page
        # Find link to podcast file (im lazy...)
        link = driver.find_element_by_xpath("//meta[@name='twitter:player:stream']").get_attribute("content")
        driver.get(link) # Go to podcast file and allow for redirect
        os.system('youtube-dl.exe {0}'.format(driver.current_url)) # Download the file
        newest = max(glob.iglob('*.[Mm][Pp]4'), key=os.path.getctime) # Get newest file
        os.rename(newest, currentPath+"\\raw_vids\\"+value.replace("/","-")+".mp4") # Rename file to correct name
        print("Finished downloading: " + value+"\n") # Output that file has finished downloading
    except Exception as e:
        print("Error fetching: "+str(value)+" at "+str(key)+"\n") # Error message
        print(e)

driver.quit() # Close the webdriver

# Add ffmpeg compression script here if not lazy

# Remove debug log made by chrome driver
try:
    os.remove("debug.log")
except Exception as e:
    pass

# Print exit messages
print("[+] Script has finished downloading all files")
print("[+] Exiting script")
exit()
