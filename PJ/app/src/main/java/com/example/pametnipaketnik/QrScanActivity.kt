package com.example.pametnipaketnik

import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.BitmapFactory
import android.net.Uri
import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import com.google.zxing.*
import com.google.zxing.common.HybridBinarizer
import com.journeyapps.barcodescanner.CaptureManager
import com.journeyapps.barcodescanner.DecoratedBarcodeView
import java.io.InputStream

class QrScanActivity : AppCompatActivity() {
    private val PICK_IMAGE_REQUEST = 2001
    private val TAG = "QrScanActivity"

    private lateinit var barcodeView: DecoratedBarcodeView
    private lateinit var capture: CaptureManager


    private val requestPermissionLauncher =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { isGranted: Boolean ->
            if (isGranted) {

                startCamera(null)
            } else {

                Toast.makeText(this, "Dovoljenje za kamero je potrebno za skeniranje.", Toast.LENGTH_LONG).show()
                finish()
            }
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d(TAG, "onCreate: QrScanActivity")
        setContentView(R.layout.activity_qr_scan)

        barcodeView = findViewById(R.id.barcode_scanner)

        when {
            ContextCompat.checkSelfPermission(this, android.Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED -> {

                startCamera(savedInstanceState)
            }
            else -> {

                requestPermissionLauncher.launch(android.Manifest.permission.CAMERA)
            }
        }

        findViewById<Button>(R.id.button_upload_image).setOnClickListener {
            val intent = Intent(Intent.ACTION_GET_CONTENT).apply { type = "image/*" }
            startActivityForResult(Intent.createChooser(intent, "Select QR Image"), PICK_IMAGE_REQUEST)
        }
    }

    private fun startCamera(savedInstanceState: Bundle?) {
        capture = CaptureManager(this, barcodeView)
        capture.initializeFromIntent(intent, savedInstanceState)
        capture.decode()

        barcodeView.decodeSingle { result ->
            if (result?.text != null) {
                val intent = Intent().apply {
                    putExtra("BOX_ID", result.text)
                }
                setResult(Activity.RESULT_OK, intent)
                finish()
            }
        }
    }


    override fun onResume() {
        super.onResume()
        if (::capture.isInitialized) {
            capture.onResume()
        }
    }

    override fun onPause() {
        super.onPause()
        if (::capture.isInitialized) {
            capture.onPause()
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        if (::capture.isInitialized) {
            capture.onDestroy()
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        if (::capture.isInitialized) {
            capture.onSaveInstanceState(outState)
        }
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)

        if (::capture.isInitialized) {
            capture.onRequestPermissionsResult(requestCode, permissions, grantResults)
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
                if (result?.text != null) {
                    val intent = Intent().apply {
                        putExtra("BOX_ID", result.text)
                    }
                    setResult(Activity.RESULT_OK, intent)
                    finish()
                } else {
                    Toast.makeText(this, "V sliki ni najdene QR kode", Toast.LENGTH_SHORT).show()
                }
            } else {
                Toast.makeText(this, "Napaka pri dekodiranju slike", Toast.LENGTH_SHORT).show()
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error scanning image: ${e.message}", e)
            Toast.makeText(this, "Napaka pri skeniranju slike: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }
}