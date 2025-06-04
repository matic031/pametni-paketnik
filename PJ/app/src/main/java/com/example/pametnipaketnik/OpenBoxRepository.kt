package com.example.pametnipaketnik

import android.content.Context
import com.example.pametnipaketnik.utils.AudioUtils
import com.example.pametnipaketnik.BuildConfig
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

object OpenBoxRepository {
    suspend fun openBoxAndPlayToken(context: Context, boxId: Int, tokenFormat: Int) = withContext(Dispatchers.IO) {
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
        val responseBody = response.body?.string()
        if (response.isSuccessful && responseBody != null) {
            val dataBase64 = JSONObject(responseBody).optString("data")
            if (dataBase64.isNotEmpty()) {
                val wavFile = AudioUtils.extractWavFromBase64Zip(context, dataBase64)
                if (wavFile != null) {
                    android.util.Log.d("OpenBoxRepository", "WAV file extracted: ${wavFile.absolutePath}")
                    AudioUtils.playWavFile(context, wavFile)
                }
            }
        }
        response.code
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