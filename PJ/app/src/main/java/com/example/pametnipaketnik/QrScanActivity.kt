package com.example.pametnipaketnik

import android.app.Activity
import android.content.Intent
import android.graphics.BitmapFactory
import android.net.Uri
import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.google.zxing.*
import com.google.zxing.common.HybridBinarizer
import com.journeyapps.barcodescanner.DecoratedBarcodeView
import java.io.InputStream

class QrScanActivity : AppCompatActivity() {
    private val PICK_IMAGE_REQUEST = 2001
    private val TAG = "QrScanActivity"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d(TAG, "onCreate: QrScanActivity")
        setContentView(R.layout.activity_qr_scan)

        val barcodeView = findViewById<DecoratedBarcodeView>(R.id.barcode_scanner)
        barcodeView.decodeContinuous { result ->
            if (result != null && result.text != null) {
                val intent = Intent()
                intent.putExtra("BOX_ID", result.text)
                setResult(Activity.RESULT_OK, intent)
                finish()
            }
        }

        findViewById<Button>(R.id.button_upload_image).setOnClickListener {
            val intent = Intent(Intent.ACTION_GET_CONTENT)
            intent.type = "image/*"
            startActivityForResult(Intent.createChooser(intent, "Select QR Image"), PICK_IMAGE_REQUEST)
        }
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        if (requestCode == PICK_IMAGE_REQUEST && resultCode == Activity.RESULT_OK && data != null) {
            val imageUri: Uri? = data.data
            if (imageUri != null) {
                scanQrFromImage(imageUri)
            }
            return
        }
        super.onActivityResult(requestCode, resultCode, data)
    }

    private fun scanQrFromImage(imageUri: Uri) {
        try {
            val inputStream: InputStream? = contentResolver.openInputStream(imageUri)
            val bitmap = BitmapFactory.decodeStream(inputStream)
            inputStream?.close()
            if (bitmap != null) {
                val intArray = IntArray(bitmap.width * bitmap.height)
                bitmap.getPixels(intArray, 0, bitmap.width, 0, 0, bitmap.width, bitmap.height)
                val source = RGBLuminanceSource(bitmap.width, bitmap.height, intArray)
                val binaryBitmap = BinaryBitmap(HybridBinarizer(source))
                val reader = MultiFormatReader()
                val result = reader.decode(binaryBitmap)
                if (result != null && result.text != null) {
                    val intent = Intent()
                    intent.putExtra("BOX_ID", result.text)
                    setResult(Activity.RESULT_OK, intent)
                    finish()
                } else {
                    Toast.makeText(this, "No QR code found in image", Toast.LENGTH_SHORT).show()
                }
            } else {
                Toast.makeText(this, "Failed to decode image", Toast.LENGTH_SHORT).show()
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error scanning image: ${e.message}", e)
            Toast.makeText(this, "Error scanning image: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }
}