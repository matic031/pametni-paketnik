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
import com.example.pametnipaketnik.databinding.ActivityFaceRegistrationBinding
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import java.io.File
import java.io.FileOutputStream
import kotlin.apply

class FaceRegistrationActivity : AppCompatActivity() {

    private lateinit var binding: ActivityFaceRegistrationBinding
    private lateinit var viewModel: FaceRegistrationViewModel
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
            binding.buttonUpload.isEnabled = true
            capturedImageUri = saveImageToCache(bitmap)

            binding.progressBar.visibility = View.VISIBLE
            binding.buttonUpload.visibility = View.INVISIBLE
            binding.buttonCapture.visibility = View.INVISIBLE
            binding.buttonPickImage.visibility = View.INVISIBLE
            capturedImageUri?.let { uploadImage(it) }
        }
    }

    private val pickImageLauncher = registerForActivityResult(
        ActivityResultContracts.GetContent()
    ) { uri ->
        if (uri != null) {
            try {
                val bitmap = MediaStore.Images.Media.getBitmap(contentResolver, uri)
                binding.imageViewFace.setImageBitmap(bitmap)
                binding.imageViewFace.clearColorFilter()
                binding.buttonUpload.isEnabled = true
                capturedImageUri = uri

                binding.progressBar.visibility = View.VISIBLE
                binding.buttonUpload.visibility = View.INVISIBLE
                binding.buttonCapture.visibility = View.INVISIBLE
                binding.buttonPickImage.visibility = View.INVISIBLE
                Toast.makeText(this, "Slika izbrana, registracija v teku...", Toast.LENGTH_SHORT)
                    .show()
                uploadImage(uri)
            } catch (e: Exception) {
                Toast.makeText(this, "Napaka pri nalaganju slike: ${e.message}", Toast.LENGTH_SHORT)
                    .show()
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityFaceRegistrationBinding.inflate(layoutInflater)
        setContentView(binding.root)

        checkFaceRegistrationStatus()

        viewModel = ViewModelProvider(this)[FaceRegistrationViewModel::class.java]

        binding.buttonCapture.setOnClickListener {
            checkCameraPermission()
        }

        binding.buttonPickImage.setOnClickListener {
            pickImageLauncher.launch("image/*")
        }

        binding.buttonUpload.setOnClickListener {
            capturedImageUri?.let { uri ->
                uploadImage(uri)
            } ?: Toast.makeText(this, "Please capture an image first", Toast.LENGTH_SHORT).show()
        }

        observeViewModel()
    }

    private fun checkFaceRegistrationStatus() {
        val sharedPreferences = getSharedPreferences("PAMETNI_PAKETNIK_PREFS", Context.MODE_PRIVATE)
        val faceRegistered = sharedPreferences.getBoolean("FACE_REGISTERED", false)

        if (faceRegistered) {
            Toast.makeText(
                this,
                "Face already registered, redirecting to verification",
                Toast.LENGTH_SHORT
            ).show()
            navigateToFaceVerification()
        }
    }

    private fun navigateToFaceVerification() {
        val intent = Intent(this, FaceVerificationActivity::class.java)
        startActivity(intent)
        finish()
    }

    private fun observeViewModel() {
        viewModel.registrationResult.observe(this) { result ->
            when (result) {
                is FaceRegistrationResult.Loading -> {
                    binding.progressBar.visibility = View.VISIBLE
                    binding.buttonUpload.isEnabled = false
                }

                is FaceRegistrationResult.Success -> {
                    binding.progressBar.visibility = View.GONE
                    binding.buttonUpload.isEnabled = true


                    val sharedPreferences =
                        getSharedPreferences("PAMETNI_PAKETNIK_PREFS", Context.MODE_PRIVATE)
                    with(sharedPreferences.edit()) {
                        putBoolean("FACE_REGISTERED", true)
                        apply()
                    }

                    Toast.makeText(this, "Face registration successful", Toast.LENGTH_LONG).show()
                    navigateToFaceVerification()
                }

                is FaceRegistrationResult.Error -> {
                    binding.progressBar.visibility = View.GONE
                    binding.buttonUpload.isEnabled = true

                    if (result.message.contains("User already registered", ignoreCase = true) ||
                        result.message.contains("already exists", ignoreCase = true)
                    ) {

                        val sharedPreferences =
                            getSharedPreferences("PAMETNI_PAKETNIK_PREFS", Context.MODE_PRIVATE)
                        with(sharedPreferences.edit()) {
                            putBoolean("FACE_REGISTERED", true)
                            apply()
                        }

                        Toast.makeText(
                            this,
                            "Face already registered, redirecting to verification",
                            Toast.LENGTH_LONG
                        ).show()
                        navigateToFaceVerification()
                    } else {
                        Toast.makeText(this, "Error: ${result.message}", Toast.LENGTH_LONG).show()
                    }
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

            ActivityCompat.shouldShowRequestPermissionRationale(
                this,
                Manifest.permission.CAMERA
            ) -> {
                Toast.makeText(
                    this,
                    "Camera permission is needed to capture your face",
                    Toast.LENGTH_LONG
                ).show()
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

    private fun uploadImage(uri: Uri) {
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

            val sharedPreferences =
                getSharedPreferences("PAMETNI_PAKETNIK_PREFS", Context.MODE_PRIVATE)
            val token = sharedPreferences.getString("AUTH_TOKEN", null)

            if (token != null) {
                viewModel.registerFace(token, imagePart)
            } else {
                Toast.makeText(
                    this,
                    "Authentication error. Please log in again.",
                    Toast.LENGTH_LONG
                ).show()
                navigateToLoginActivity()
            }
        } catch (e: Exception) {
            Toast.makeText(this, "Error processing image: ${e.message}", Toast.LENGTH_LONG).show()
        }
    }

    private fun navigateToMainActivity() {
        val intent = Intent(this, MainActivity::class.java)
        startActivity(intent)
        finish()
    }

    private fun navigateToLoginActivity() {
        val intent = Intent(this, LoginActivity::class.java)
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        startActivity(intent)
        finish()
    }
}

