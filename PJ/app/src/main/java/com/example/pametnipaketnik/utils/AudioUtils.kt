package com.example.pametnipaketnik.utils

import android.content.Context
import android.media.MediaPlayer
import android.util.Base64
import android.util.Log
import android.widget.Toast
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream
import java.util.zip.ZipInputStream

object AudioUtils {
    private const val TAG = "AudioUtils"

    fun extractWavFromBase64Zip(context: Context, base64Zip: String): File? {
        Log.d(TAG, "extractWavFromBase64Zip: Decoding base64 zip")
        return try {
            val zipBytes = Base64.decode(base64Zip, Base64.DEFAULT)
            val tempZip = File.createTempFile("token", ".zip", context.cacheDir)
            tempZip.writeBytes(zipBytes)
            val zipInput = ZipInputStream(FileInputStream(tempZip))
            var wavFile: File? = null
            var entry = zipInput.nextEntry
            while (entry != null) {
                if (entry.name.endsWith(".wav")) {
                    wavFile = File.createTempFile("token", ".wav", context.cacheDir)
                    FileOutputStream(wavFile).use { out ->
                        zipInput.copyTo(out)
                    }
                    break
                }
                entry = zipInput.nextEntry
            }
            zipInput.close()
            wavFile
        } catch (e: Exception) {
            Log.e(TAG, "extractWavFromBase64Zip error: ${e.message}", e)
            null
        }
    }

    fun playWavFile(context: Context, wavFile: File) {
        Log.d(TAG, "playWavFile: Playing WAV file: ${wavFile.absolutePath}")
        try {
            val mediaPlayer = MediaPlayer()
            mediaPlayer.setDataSource(wavFile.absolutePath)
            mediaPlayer.prepare()
            mediaPlayer.start()
            mediaPlayer.setOnCompletionListener {
                it.release()
                Toast.makeText(context, "Token played", Toast.LENGTH_SHORT).show()
            }
        } catch (e: Exception) {
            Log.e(TAG, "playWavFile error: ${e.message}", e)
            Toast.makeText(context, "Failed to play token: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }
}