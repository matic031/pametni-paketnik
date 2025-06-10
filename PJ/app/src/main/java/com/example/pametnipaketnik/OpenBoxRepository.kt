package com.example.pametnipaketnik

import android.content.Context
import android.net.Uri // Dodan import
import android.util.Log
import com.example.pametnipaketnik.utils.AudioUtils
import com.example.pametnipaketnik.BuildConfig
import com.example.pametnipaketnik.data.CreateLogRequest
import com.example.pametnipaketnik.network.RetrofitInstance
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.security.SecureRandom
import java.security.cert.X509Certificate
import javax.net.ssl.SSLContext
import javax.net.ssl.TrustManager
import javax.net.ssl.X509TrustManager
import com.example.pametnipaketnik.data.TokenManager

object OpenBoxRepository {

    suspend fun openBoxAndLog(context: Context, boxId: Int, tokenFormat: Int, onPlaybackFinished: () -> Unit) {
        var responseCode: Int = -1
        var status: String = "FAILURE"
        var message: String = "Unknown error occurred"

        try {
            val direct4meResponse = openBoxAndPlayTokenInternal(context, boxId, tokenFormat, onPlaybackFinished)
            responseCode = direct4meResponse.first
            message = direct4meResponse.second

            if (responseCode in 200..299) {

            }

        } catch (e: Exception) {
            message = "Failed to call Direct4.me API: ${e.message}"
            Log.e("OpenBoxRepo", message, e)
            onPlaybackFinished()
        }
    }

    suspend fun logAttempt(context: Context, boxId: Int, status: String, message: String, responseCode: Int) {
        val token = TokenManager.getToken(context)
        if (token == null) {
            Log.e("OpenBoxRepo", "Cannot log attempt: user not logged in (token is null)")
            return
        }
        try {
            val logRequest = CreateLogRequest(boxId, status, message, responseCode)
            val response = RetrofitInstance.getApiService(context).createLog(logRequest)
            if (response.isSuccessful) {
                Log.d("OpenBoxRepo", "Log successfully created for box ID $boxId")
            } else {
                Log.e("OpenBoxRepo", "Failed to create log: ${response.code()} - ${response.errorBody()?.string()}")
            }
        } catch (e: Exception) {
            Log.e("OpenBoxRepo", "Exception while creating log", e)
        }
    }

    private suspend fun openBoxAndPlayTokenInternal(context: Context, boxId: Int, tokenFormat: Int, onPlaybackFinished: () -> Unit): Pair<Int, String> = withContext(Dispatchers.IO) {
        val client = getUnsafeOkHttpClient()
        val url = "https://api-d4me-stage.direct4.me/sandbox/v1/Access/openbox"
        val json = """{"boxId": $boxId, "tokenFormat": $tokenFormat}""".trimIndent()
        val body = json.toRequestBody("application/json".toMediaType())
        val bearerToken = BuildConfig.BEARER_TOKEN

        val request = Request.Builder()
            .url(url)
            .addHeader("Content-Type", "application/json")
            .addHeader("Authorization", "Bearer $bearerToken")
            .post(body)
            .build()

        val response = client.newCall(request).execute()
        val responseBodyString = response.body?.string()

        var message: String
        if (response.isSuccessful && responseBodyString != null) {
            val dataBase64 = JSONObject(responseBodyString).optString("data")
            if (dataBase64.isNotEmpty()) {
                val wavFile = AudioUtils.extractWavFromBase64Zip(context, dataBase64)
                if (wavFile != null) {
                    // Predamo callback naprej v AudioUtils
                    withContext(Dispatchers.Main) {
                        AudioUtils.playWavFile(context, Uri.fromFile(wavFile), onPlaybackFinished)
                    }
                    message = "Token playing."
                } else {
                    message = "Failed to extract WAV file from response."
                    withContext(Dispatchers.Main) { onPlaybackFinished() }
                }
            } else {
                message = "Response successful, but 'data' field was empty."
                withContext(Dispatchers.Main) { onPlaybackFinished() }
            }
        } else {
            message = "API call failed. Code: ${response.code}. Body: ${responseBodyString ?: "null"}"
            withContext(Dispatchers.Main) { onPlaybackFinished() }
        }

        return@withContext Pair(response.code, message)
    }


    private fun getUnsafeOkHttpClient(): OkHttpClient {
        val trustAllCerts = arrayOf<TrustManager>(
            object : X509TrustManager {
                override fun checkClientTrusted(chain: Array<out X509Certificate>?, authType: String?) {}
                override fun checkServerTrusted(chain: Array<out X509Certificate>?, authType: String?) {}
                override fun getAcceptedIssuers(): Array<X509Certificate> = arrayOf()
            }
        )
        val sslContext = SSLContext.getInstance("SSL")
        sslContext.init(null, trustAllCerts, SecureRandom())
        val sslSocketFactory = sslContext.socketFactory
        return OkHttpClient.Builder()
            .sslSocketFactory(sslSocketFactory, trustAllCerts[0] as X509TrustManager)
            .hostnameVerifier { _, _ -> true }
            .build()
    }

    fun extractBoxId(qrContent: String?): Int? {
        if (qrContent == null) return null
        qrContent.toIntOrNull()?.let { return it }
        val regex = Regex("""\b\d{6,}\b""")
        val match = regex.find(qrContent)
        return match?.value?.toIntOrNull()
    }
}