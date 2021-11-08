#### Account Info

You'll need to add your Spotify and deezer account information to the `account_info.json` file. This file will be generated upon the first execution of `main.py`. Once it's there, gather the information following the steps below and paste it in. To verify the `.json` file is still formatted correctly, you can use https://jsonlint.com.

You are not giving me your password! These tokens are used to *avoid* sharing your password. All of this data is stored locally in the `account_info.json` file, and is sent exclusively to Spotify or deezer. This is safe.

##### Finding `SPOTIFY_USERNAME`

 1. Go to https://open.spotify.com/. Sign into your account.
 2. In the top right, click your display name, then `Account`.
 3. Your `Username` should be the first field on this page.

##### Finding `SPOTIFY_CLIENT_ID`

 1. Go to https://developer.spotify.com/dashboard/login. Sign into your account.
 2. Select `CREATE AN APP`.
 3. The `App name` and `App description` are irrelevant. Click `CREATE` when you're ready.
 4. In the application's menu, click `Edit Settings`. Add the URL `https://example.com` in the `Redirect URIs` field. Save it.
 5. Your `Client ID` will be near the top right, under the app name/description.

##### Finding `SPOTIFY_CLIENT_SECRET`

 1. In the same app you created above, click `SHOW CLIENT SECRET`.
 2. Your `Client Secret` will appear.
 
##### Finding `DEEZER_ARL`

(Copied from [here](https://web.archive.org/web/20200917142534/https://notabug.org/RemixDevs/DeezloaderRemix/wiki/Login+via+userToken))

###### Chrome

1. Open Chrome.
2. Go to [deezer.com](https://deezer.com). Log into your account.
3. Click the lock icon to the left of the URL in the address bar.
4. Click on Cookies > deezer.com > Cookies > arl
5. Select the text next to Content and copy it.

###### Firefox

1. Open Firefox.
2. Go to [deezer.com](https://deezer.com). Log into your account.
3. After logging in, press F12 to open up Developer Tools.
4. Open the Storage tab (if you don't see it, click the double arrow).
5. Open the Cookies dropdown.
6. Select https://www.deezer.com
7. Find the `arl` cookie. It should be 192 chars long.
8. Double-click the **value** and copy it.

You will have your ARL copied.

##### Example

In the end, your `account_info.json` file should look something like this:

```
{
    "SPOTIFY_USERNAME": "sf08ug804h302gn02200g42",
    "SPOTIFY_CLIENT_ID": "gi8h492gneisowo3ggs",
    "SPOTIFY_CLIENT_SECRET": "fgn8932hfiewnoi32g42",
    "DEEZER_ARL": "g4j02g9jeiodsjgo4ww"
}
```