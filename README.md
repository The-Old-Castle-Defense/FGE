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

# Guide to Creating a Frame with FGE

## Step 0: Open Google Form by following the link
Click here: https://docs.google.com/forms/d/e/1FAIpQLSfhvuW9ITz3fuAo4R78T3ksulLfrvHTWX6_3wynR_lUZUqgFw/viewform

## Step 1: Enter the FrameID
**Description:** FrameID is a unique identifier for your Frame. Think of it as a unique name that distinguishes your Frame from others.

**Rules:** It must be unique, that is, different from other FrameIDs in the Frame Group (about the Frame Group in the next step).

**Example:** `saturday` or `test_1`

## Step 2: Enter the GroupID:
**Description:** GroupID is an identifier used to access a Frame Group (a set of Frames with a FrameID).

**Rules:** Try to come up with an ID that will combine all your FrameIDs. For example, if the set of your FrameIDs is <Saturday> and <Sunday>, then it is logical to call the GroupID "Weekend". Don't forget this ID, it will still be useful to you.

**Example:** `weekend`

_Your Frame Group will be accessible via `https://fc.theoldcastle.xyz/frame/{GroupID}`_

## Step 3: Title
**Description:** Give your Frame a title. This should be succinct and reflective of the content or the action encouraged by the Frame.

**Rules:** It may not be unique.

**Example:** `View the days of the weekend!`

## Step 4: Buttons
**Description:** Define the buttons you want to include. You need at least one button.

**Rules:** Each button array consists of the button name, the action type ("post" or "link"), and optionally, the URL if the action type is "link":
```
[["Btn1_name", "post"], ["Btn2_name", "post"], ["Btn3_name", "link", "link"]]
```

**Example:** `[["👉The next day", "post"]]`

## Step 5: Image and Text Positioning
**Description:** Specify where you want your image and text to appear within the Frame.

**Rules:** The format is:
```
[["image_url"], [x, y, "Text", "#Color", FONT_SIZE]]`
```

**Example:** `[["https://i.ibb.co/Km2czWx/saturday.png"], [33, 33, "It’s Saturday!", "#de7676", 16]]`

## Step 6: Input [Text Placeholder] (Optional)
**Description:** An input field for user interaction, specify a placeholder text.

**Rules:** This field is optional if you do not need to receive a response from the user in the frame.

**Example:** `Write a "+" if you like this day`

## Step 7: Next Frame URL (URL will navigate to your next Frame)
**Description:** The next frame, which is part of a sequence in a Group of Frames, i.e. you want to redirect users to another Frame after the interaction.

**Rules:** 
- Specify the Next URL in the format: `https://fc.theoldcastle.xyz/api/next/{FrameID}`
- For buttons that navigate to other Frames, append: `?btn_1={frame_link}&btn_2={frame_link}`

**Example:** `https://fc.theoldcastle.xyz/api/next/saturday?btn_1=sunday`

## Step 8: Open Warpcast Dev Tools by following the link
Click here: https://warpcast.com/~/developers/frames

## Step 9: Put the link to the Warpcast Dev Tools
Do you remember GroupID? Add it to the link template and paste it into the "URL" field

**Template:** `https://fc.theoldcastle.xyz/frame/{GroupID}`

**Example:** `https://fc.theoldcastle.xyz/frame/weekend`

Ready! Now you can test the operation of your Frame

