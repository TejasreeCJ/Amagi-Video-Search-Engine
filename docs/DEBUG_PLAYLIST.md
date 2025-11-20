# Debugging Playlist Issues

## Quick Test

Run this command to test your playlist URL:

```bash
python test_playlist_url.py "https://www.youtube.com/playlist?list=PLbRMhDVUMngfK1HrAqu6tnKEVHwC3ILuE"
```

This will tell you:
- If the playlist is accessible
- How many videos are in it
- If there are any errors

## Common Issues and Solutions

### 1. Private Playlist
**Problem**: Playlist is private or requires authentication

**Solution**: 
- Make sure the playlist is set to "Public" or "Unlisted" in YouTube
- Check the playlist privacy settings

### 2. No Captions Available
**Problem**: Videos don't have automatic captions or subtitles

**Solution**:
- The scraper needs videos with captions/subtitles
- Check if videos have captions enabled on YouTube
- Try a different playlist that you know has captions

### 3. Outdated yt-dlp
**Problem**: yt-dlp version might be outdated

**Solution**:
```bash
pip install --upgrade yt-dlp
```

### 4. Region Restrictions
**Problem**: Videos might be blocked in your region

**Solution**:
- Try accessing the playlist in a browser first
- Check if videos are available in your region

### 5. Invalid Playlist URL
**Problem**: URL format might be incorrect

**Solution**:
- Make sure the URL is a full playlist URL
- Format should be: `https://www.youtube.com/playlist?list=PLAYLIST_ID`
- Or: `https://www.youtube.com/watch?v=VIDEO_ID&list=PLAYLIST_ID`

## Testing Steps

1. **Test the URL**:
   ```bash
   python test_playlist_url.py "YOUR_PLAYLIST_URL"
   ```

2. **Check backend logs**:
   - When you try to process the playlist, check the terminal where the server is running
   - Look for error messages or warnings

3. **Try a known working playlist**:
   - Test with a public playlist you know has captions
   - Example: NPTEL playlists usually have captions

## What to Check

1. ✅ Playlist is public/unlisted
2. ✅ Videos have captions/subtitles enabled
3. ✅ yt-dlp is up to date
4. ✅ Internet connection is working
5. ✅ Playlist URL is correct

## Getting Better Error Messages

The improved code now provides:
- Detailed error messages
- Progress information
- Which videos are being processed
- Which videos have transcripts

Check the backend server terminal for detailed logs when processing.

