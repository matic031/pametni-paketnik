package com.example.pametnipaketnik

import android.content.Context
import android.util.Log
import com.example.pametnipaketnik.utils.AudioUtils
import com.example.pametnipaketnik.BuildConfig
import com.example.pametnipaketnik.data.CreateLogRequest
import com.example.pametnipaketnik.network.RetrofitInstance
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.coroutineScope
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

    suspend fun openBoxAndLog(context: Context, boxId: Int, tokenFormat: Int) {
        coroutineScope {
            var responseCode: Int = -1
            var status: String = "FAILURE"
            var message: String = "Unknown error occurred"

            try {
                // Klic na Direct4.me API
                val direct4meResponse = openBoxAndPlayTokenInternal(context, boxId, tokenFormat)
                responseCode = direct4meResponse.first
                message = direct4meResponse.second

                if (responseCode in 200..299) {
                    status = "SUCCESS"
                }else{
                    status = "FAILURE"
                }

            } catch (e: Exception) {
                // Ujamemo morebitne napake pri klicu na direct4.me
                message = "Failed to call Direct4.me API: ${e.message}"
                Log.e("OpenBoxRepo", message, e)
            } finally {
                // V vsakem primeru (uspeh ali neuspeh) poskusimo shraniti log
                logAttempt(context, boxId, status, message, responseCode)
            }
        }
    }

    private suspend fun logAttempt(context: Context, boxId: Int, status: String, message: String, responseCode: Int) {
        val token = TokenManager.getToken(context) // Pridobi shranjen JWT žeton!
        if (token == null) {
            Log.e("OpenBoxRepo", "Cannot log attempt: user not logged in (token is null)")
            return
        }

        try {
            val logRequest = CreateLogRequest(
                boxId = boxId,
                status = status,
                message = message,
                responseCode = responseCode
            )
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

    private suspend fun openBoxAndPlayTokenInternal(context: Context, boxId: Int, tokenFormat: Int): Pair<Int, String> = withContext(Dispatchers.IO) {
        val client = getUnsafeOkHttpClient()
        val url = "https://api-d4me-stage.direct4.me/sandbox/v1/Access/openbox"
        val json = """
            {
                "boxId": $boxId,
                "tokenFormat": $tokenFormat
            }
        """.trimIndent()
        val body = json.toRequestBody("application/json".toMediaType())

        val bearerToken = BuildConfig.BEARER_TOKEN
        android.util.Log.d("loaded", "bearer : $bearerToken")

        val request = Request.Builder()
            .url(url)
            .addHeader("Content-Type", "application/json")
            .addHeader("Authorization", "Bearer $bearerToken")
            .post(body)
            .build()

        android.util.Log.d("OpenBoxRepository", "Request: $request")

        val response = client.newCall(request).execute()
        val responseBodyString = response.body?.string()

        var message: String
        if (response.isSuccessful && responseBodyString != null) {
            val dataBase64 = JSONObject(responseBodyString).optString("data")
            if (dataBase64.isNotEmpty()) {
                val wavFile = AudioUtils.extractWavFromBase64Zip(context, dataBase64)
                if (wavFile != null) {
                    AudioUtils.playWavFile(context, wavFile)
                    message = "Token successfully played."
                } else {
                    message = "Failed to extract WAV file from response."
                }
            } else {
                message = "Response successful, but 'data' field was empty."
            }
        } else {
            message = "API call failed. Code: ${response.code}. Body: ${responseBodyString ?: "null"}"
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