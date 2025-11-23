# Solutions for "No Videos with Transcripts" Error

## Problem
Your playlist is accessible and videos are found, but **none of the videos have transcripts/captions available**.

## Why This Happens
- Videos don't have automatic captions enabled
- Videos don't have manual subtitles
- YouTube hasn't generated automatic captions yet
- Captions might be disabled by the video owner

## Solutions

### Solution 1: Check Which Videos Have Transcripts

Run this script to see which videos in your playlist have transcripts:

```bash
python check_playlist_transcripts.py "YOUR_PLAYLIST_URL"
```

This will show you:
- Which videos have transcripts (can be processed)
- Which videos don't have transcripts (cannot be processed)

### Solution 2: Use a Playlist with Captions

Try a playlist that you know has automatic captions. Here are some examples:

**NPTEL Playlists (usually have captions):**
- Physics: `https://www.youtube.com/playlist?list=PLbMVogVj5nJQ2vsW_hmyvVfO4GYWaaPpO`
- Computer Science: Search for "NPTEL" playlists on YouTube

**How to find playlists with captions:**
1. Go to YouTube
2. Search for educational content (lectures, tutorials)
3. Look for videos with the CC (Closed Captions) icon
4. Check if automatic captions are available

### Solution 3: Enable Captions on Your Videos

If you own the videos:

1. Go to YouTube Studio
2. Select the video
3. Go to "Subtitles" section
4. Enable "Automatic captions"
5. Wait for YouTube to generate captions (may take time)
6. Process the playlist again

### Solution 4: Process Videos That Have Transcripts

If some videos in your playlist have transcripts:

1. The system will process only videos with transcripts
2. Videos without transcripts will be skipped
3. You'll get a message showing how many videos were processed

However, if **ALL** videos lack transcripts, you'll get this error.

### Solution 5: Enable Whisper Transcript Generation

**NEW!** Use AI to generate transcripts for videos without captions:

1. **Enable Whisper in your environment**:
   ```bash
   # In your .env file
   WHISPER_ENABLED=true
   WHISPER_MODEL_SIZE=tiny
   ```

2. **Install Whisper dependencies**:
   ```bash
   pip install openai-whisper torch torchaudio
   ```

3. **Restart the server** and process your playlist again

The system will now automatically generate transcripts using AI when YouTube captions aren't available.

See [`docs/WHISPER_INTEGRATION.md`](WHISPER_INTEGRATION.md) for detailed setup instructions.

### Solution 6: Use a Test Playlist

Try processing a small test playlist first:

1. Create a playlist with 2-3 videos that you know have captions
2. Process that playlist to test the system
3. Once it works, try larger playlists

## How to Verify a Video Has Captions

1. Open the video on YouTube
2. Click the "CC" (Closed Captions) button
3. If captions appear, the video has transcripts
4. If no captions appear, the video doesn't have transcripts

## Expected Behavior

- **If videos have transcripts**: Processing will work
- **If no videos have transcripts**: You'll get the error message
- **If some videos have transcripts**: Only those will be processed

## Next Steps

1. **Try Whisper (Recommended)**: Enable AI transcript generation - see Solution 5 above
2. **Check your playlist**: Run `python check_playlist_transcripts.py "YOUR_URL"`
3. **Try a different playlist**: Use one with known captions
4. **Check YouTube**: Verify videos have the CC icon enabled
5. **Wait and retry**: If captions are being generated, wait and try again

## Example: Testing with NPTEL

Try this NPTEL playlist (usually has captions):

```bash
python check_playlist_transcripts.py "https://www.youtube.com/playlist?list=PLbMVogVj5nJQ2vsW_hmyvVfO4GYWaaPpO"
```

If this works, your system is fine - the issue is just that your original playlist doesn't have captions.

