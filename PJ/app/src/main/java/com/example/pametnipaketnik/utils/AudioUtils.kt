package com.example.pametnipaketnik.utils

import android.content.Context
import android.media.MediaPlayer
import android.net.Uri // Spremenil sem import iz File v Uri, ker je bolj fleksibilno
import android.util.Base64
import android.util.Log
import java.io.File
import java.io.FileOutputStream
import java.util.zip.ZipInputStream

object AudioUtils {

    fun extractWavFromBase64Zip(context: Context, base64String: String): File? {
        return try {
            val decodedBytes = Base64.decode(base64String, Base64.DEFAULT)
            val zipInputStream = ZipInputStream(decodedBytes.inputStream())
            val zipEntry = zipInputStream.nextEntry
            if (zipEntry != null && !zipEntry.isDirectory && zipEntry.name.endsWith(".wav")) {
                val outputFile = File(context.cacheDir, zipEntry.name)
                FileOutputStream(outputFile).use { fileOutputStream ->
                    zipInputStream.copyTo(fileOutputStream)
                }
                zipInputStream.closeEntry()
                zipInputStream.close()
                Log.d("AudioUtils", "WAV file extracted to: ${outputFile.absolutePath}")
                outputFile
            } else {
                Log.e("AudioUtils", "No WAV file found in ZIP.")
                null
            }
        } catch (e: Exception) {
            Log.e("AudioUtils", "Failed to extract WAV file", e)
            null
        }
    }


    fun playWavFile(context: Context, wavFileUri: Uri, onCompletionCallback: () -> Unit) {
        Log.d("AudioUtils", "Playing WAV file from URI: $wavFileUri")
        try {
            val mediaPlayer = MediaPlayer.create(context, wavFileUri)
            mediaPlayer?.setOnCompletionListener {
                Log.d("AudioUtils", "Playback completed.")
                onCompletionCallback()
                it.release()
            }
            mediaPlayer?.setOnErrorListener { _, what, extra ->
                Log.e("AudioUtils", "MediaPlayer error: what=$what, extra=$extra")
                onCompletionCallback()
                true
            }
            mediaPlayer?.start()
        } catch (e: Exception) {
            Log.e("AudioUtils", "Failed to play WAV file", e)
            onCompletionCallback()
        }
    }
}