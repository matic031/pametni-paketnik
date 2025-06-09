package com.example.pametnipaketnik

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.net.Uri
import android.os.Bundle
import android.provider.MediaStore
import android.view.View
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.ViewModelProvider
import com.example.pametnipaketnik.databinding.ActivityFaceVerificationBinding
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.File
import java.io.FileOutputStream
import kotlin.apply
import kotlin.collections.remove
import kotlin.or

class FaceVerificationActivity : AppCompatActivity() {

    private lateinit var binding: ActivityFaceVerificationBinding
    private lateinit var viewModel: FaceVerificationViewModel
    private var capturedImageUri: Uri? = null

    private val cameraPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            openCamera()
        } else {
            Toast.makeText(this, "Camera permission is required", Toast.LENGTH_LONG).show()
        }
    }

    private val takePictureLauncher = registerForActivityResult(
        ActivityResultContracts.TakePicturePreview()
    ) { bitmap ->
        if (bitmap != null) {
            binding.imageViewFace.setImageBitmap(bitmap)
            binding.imageViewFace.clearColorFilter()
            binding.buttonVerify.isEnabled = true
            capturedImageUri = saveImageToCache(bitmap)
            binding.progressBar.visibility = View.VISIBLE
            binding.buttonVerify.visibility = View.INVISIBLE
            binding.buttonCapture.visibility = View.INVISIBLE
            binding.buttonPickImage.visibility = View.INVISIBLE

            capturedImageUri?.let { verifyFace(it) }
        }
    }

    private val pickImageLauncher = registerForActivityResult(
        ActivityResultContracts.GetContent()
    ) { uri ->
        if (uri != null) {
            try {
                binding.imageViewFace.setImageURI(uri)
                binding.imageViewFace.clearColorFilter()
                binding.buttonVerify.isEnabled = true
                capturedImageUri = uri

                Toast.makeText(this, "Image selected. Click 'Verify Face' to continue.", Toast.LENGTH_SHORT).show()
            } catch (e: Exception) {
                Toast.makeText(this, "Failed to load image: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityFaceVerificationBinding.inflate(layoutInflater)
        setContentView(binding.root)

        viewModel = ViewModelProvider(this)[FaceVerificationViewModel::class.java]

        binding.buttonCapture.setOnClickListener {
            checkCameraPermission()
        }

        binding.buttonPickImage.setOnClickListener {
            pickImageLauncher.launch("image/*")
        }

        binding.buttonVerify.setOnClickListener {
            capturedImageUri?.let { uri ->
                verifyFace(uri)
            } ?: Toast.makeText(this, "Please capture an image first", Toast.LENGTH_SHORT).show()
        }

        observeViewModel()
    }

    private fun observeViewModel() {
        viewModel.verificationResult.observe(this) { result ->
            when (result) {
                is FaceVerificationResult.Loading -> {
                    binding.progressBar.visibility = View.VISIBLE
                    binding.buttonVerify.isEnabled = false
                }
                is FaceVerificationResult.Success -> {
                    binding.progressBar.visibility = View.GONE
                    binding.buttonVerify.visibility = View.VISIBLE
                    binding.buttonCapture.visibility = View.VISIBLE
                    binding.buttonPickImage.visibility = View.VISIBLE
                    if (result.response.verified) {
                        Toast.makeText(this, "Face verification successful", Toast.LENGTH_LONG).show()
                        navigateToMainActivity()
                    } else {
                        Toast.makeText(this, "Face verification failed. Score: ${result.response.similarity_score}", Toast.LENGTH_LONG).show()
                        binding.buttonVerify.isEnabled = true
                    }
                }
                is FaceVerificationResult.Error -> {
                    binding.progressBar.visibility = View.GONE
                    binding.buttonVerify.visibility = View.VISIBLE
                    binding.buttonCapture.visibility = View.VISIBLE
                    binding.buttonPickImage.visibility = View.VISIBLE
                    binding.buttonVerify.isEnabled = true
                    Toast.makeText(this, "Error: ${result.message}", Toast.LENGTH_LONG).show()
                }
            }
        }
    }

    private fun checkCameraPermission() {
        when {
            ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) ==
                    PackageManager.PERMISSION_GRANTED -> {
                openCamera()
            }
            ActivityCompat.shouldShowRequestPermissionRationale(this, Manifest.permission.CAMERA) -> {
                Toast.makeText(this, "Camera permission is needed to verify your face", Toast.LENGTH_LONG).show()
                cameraPermissionLauncher.launch(Manifest.permission.CAMERA)
            }
            else -> {
                cameraPermissionLauncher.launch(Manifest.permission.CAMERA)
            }
        }
    }

    private fun openCamera() {
        takePictureLauncher.launch(null)
    }

    private fun saveImageToCache(bitmap: Bitmap): Uri {
        val file = File(cacheDir, "face_image_${System.currentTimeMillis()}.jpg")
        FileOutputStream(file).use { out ->
            bitmap.compress(Bitmap.CompressFormat.JPEG, 100, out)
        }
        return Uri.fromFile(file)
    }

    private fun verifyFace(uri: Uri) {
        try {
            val inputStream = contentResolver.openInputStream(uri)
            val tempFile = File(cacheDir, "temp_image_${System.currentTimeMillis()}.jpg")

            inputStream?.use { input ->
                FileOutputStream(tempFile).use { output ->
                    input.copyTo(output)
                }
            }

            val requestFile = tempFile.asRequestBody("image/jpeg".toMediaTypeOrNull())
            val imagePart = MultipartBody.Part.createFormData("image", tempFile.name, requestFile)

            val sharedPreferences = getSharedPreferences("PAMETNI_PAKETNIK_PREFS", Context.MODE_PRIVATE)
            val token = sharedPreferences.getString("AUTH_TOKEN", null)
            val userId = sharedPreferences.getString("USER_ID", null)

            android.util.Log.e("FaceVerificationActivity", "userid is: " + userId)

            if (token != null && !userId.isNullOrEmpty()) {
                val userIdBody = userId.toRequestBody("text/plain".toMediaTypeOrNull())

                viewModel.verifyFace(token, userIdBody, imagePart)
            } else {
                Toast.makeText(this, "Authentication error. Please log in again.", Toast.LENGTH_LONG).show()
                navigateToLoginActivity()
            }
        } catch (e: Exception) {
            Toast.makeText(this, "Error processing image: ${e.message}", Toast.LENGTH_LONG).show()
            binding.progressBar.visibility = View.GONE
        }
    }
    private fun navigateToMainActivity() {
        val intent = Intent(this, MainActivity::class.java)
        startActivity(intent)
        finish()
    }

    private fun navigateToLoginActivity() {
        val sharedPreferences = getSharedPreferences("PAMETNI_PAKETNIK_PREFS", Context.MODE_PRIVATE)
        with(sharedPreferences.edit()) {
            remove("AUTH_TOKEN")
            remove("FACE_VERIFIED")
            remove("USER_ID")
            apply()
        }

        val intent = Intent(this, LoginActivity::class.java)
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        startActivity(intent)
        finish()
    }
}

