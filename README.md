# FGE - Frame Generator Engine - Farcaster Frames Client
FGE(Frame Generator Engine) - Farcaster Frames Client. Create Frames with No Code Knowledge, all you need is Google Spreadsheet. Fill it, upload your image and share with your friends around Warpcast. *Do not forget to tag @tocd when you'll become success.*

TOCD will support your Frames no matter what. Only for people good.

## Live Video

<div>
    <a href="https://www.loom.com/share/578b304830214e9ba07d1836a46bf326">
      <p>How to create Frames with NO Code Skills - It's Easy with FGE. Top Frames on Farcaster with FGE - Watch Video</p>
    </a>
    <a href="https://www.loom.com/share/578b304830214e9ba07d1836a46bf326">
      <img style="max-width:300px;" src="https://cdn.loom.com/sessions/thumbnails/578b304830214e9ba07d1836a46bf326-with-play.gif">
    </a>
  </div>

## Farcaster Frames made by FGE or forked by FGE
https://github.com/The-Old-Castle-Defense/FGE/tree/main/fge_app

#### Cross-Chain Bridge BASE <> OPTIMISM made with DeBridge integration
https://github.com/The-Old-Castle-Defense/FGE/tree/main/frames/frame_cross_chain_trades

#### OnChain Events of TOCD Protocol with TheGraph
https://github.com/The-Old-Castle-Defense/FGE/tree/main/frames/frame_onchain_events
Video: https://www.loom.com/share/ea620424706d400690b6ad85a254d408

#### Frames Analytics & Farcaster's Data with Pinata
https://github.com/The-Old-Castle-Defense/FGE/blob/main/frames/frame_onchain_events/pinata.py
Video: https://www.loom.com/share/1434ee81850546068bd73cfec0901b35

# Setting Up Google Sheets API Credentials
To integrate Google Sheets with the Farcaster's Frame Generator Engine, you'll need to create a credentials.json file. This file enables your application to authenticate with Google's API and interact with Google Sheets. Follow these steps to generate your credentials file:

### 1. Google Cloud Project: 
If you don't already have a Google Cloud Project, create one at the Google Cloud Console. Name it accordingly to easily recognize it in the future.


### 2. Enable Google Sheets API: 
Navigate to the "APIs & Services > Dashboard" section. Click on "+ ENABLE APIS AND SERVICES" to search for and enable the Google Sheets API for your project.

### 3. Create Credentials:
* After enabling the API, go to "APIs & Services > Credentials".
* Click on "+ CREATE CREDENTIALS" and select "Service account" from the dropdown menu.
* Follow the on-screen instructions to create a service account. Note the service account ID; it usually looks like an email address.
* Once created, click on the service account in the list, navigate to the "Keys" tab, and click on "Add Key > Create new key".
* Choose "JSON" as the key type and click "Create". This action downloads the credentials.json file to your computer.
### 4. Share Google Sheet: 
Finally, share the Google Sheet with your service account using the service account ID (email) you noted earlier. This step grants the necessary permissions for the service account to access and modify the Google Sheet.

Use credentials.json with Farcaster's Frame Generator Engine: Place the credentials.json file in the specified directory of your project or configure its path according to the engine's documentation.

By following these steps, you should have the credentials.json file needed to authenticate and interact with Google Sheets through the Farcaster's Frame Generator Engine.

**Online Guide with images**: https://medium.com/@a.marenkov/how-to-get-credentials-for-google-sheets-456b7e88c430


