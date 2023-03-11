package hk.hku.fyp.camera_notification_system

import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.widget.Toast

class MainActivity : AppCompatActivity() {

    private var serverAddress: String = "http://10.70.44.77:5000"
    private var userToken: String? = null


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val loginButton = findViewById<Button>(R.id.menu_login)
        val notificationButton = findViewById<Button>(R.id.menu_notifications)
        val addReportButton = findViewById<Button>(R.id.menu_addReports)
        val removeReport = findViewById<Button>(R.id.menu_removeReports)
        val addCameraButton = findViewById<Button>(R.id.menu_addCamera)
        val addOfficerButton = findViewById<Button>(R.id.menu_addOfficer)

        userToken = intent.getStringExtra("userToken")

//        Toast.makeText(this, userToken!!, Toast.LENGTH_SHORT).show()



        loginButton!!.setOnClickListener {
            val intent = Intent(this, LoginPage::class.java)
            intent.putExtra("serverAddress",serverAddress)
            startActivity(intent)
        }
        notificationButton!!.setOnClickListener {
            if (userToken != null) {
                val intent = Intent(this, NotificationWatchPage::class.java)
                intent.putExtra("serverAddress", serverAddress)
                intent.putExtra("userToken", userToken!!)
                startActivity(intent)
            }else{
                val intent = Intent(this, LoginPage::class.java)
                intent.putExtra("serverAddress",serverAddress)
                startActivity(intent)
            }
        }
        addReportButton!!.setOnClickListener {
            if (userToken != null) {
                val intent = Intent(this, AddReport::class.java)
                intent.putExtra("serverAddress", serverAddress)
                intent.putExtra("userToken", userToken!!)
                startActivity(intent)
            }else{
                val intent = Intent(this, LoginPage::class.java)
                intent.putExtra("serverAddress",serverAddress)
                startActivity(intent)
            }
        }
        removeReport!!.setOnClickListener {
            if (userToken != null) {
                val intent = Intent(this, RemoveReport::class.java)
                intent.putExtra("serverAddress", serverAddress)
                intent.putExtra("userToken", userToken!!)
                startActivity(intent)
            }else{
                val intent = Intent(this, LoginPage::class.java)
                intent.putExtra("serverAddress",serverAddress)
                startActivity(intent)
            }
        }
        addCameraButton!!.setOnClickListener {
            if (userToken != null) {
            val intent = Intent(this, AddCamera::class.java)
            intent.putExtra("serverAddress", serverAddress)
            intent.putExtra("userToken", userToken!!)
            startActivity(intent)
            } else {
                val intent = Intent(this, LoginPage::class.java)
                intent.putExtra("serverAddress",serverAddress)
                startActivity(intent)
            }
        }
        addOfficerButton!!.setOnClickListener {
            if (userToken != null) {
                val intent = Intent(this, AddOfficer::class.java)
                intent.putExtra("serverAddress", serverAddress)
                intent.putExtra("userToken", userToken!!)
                startActivity(intent)
            }else{
                val intent = Intent(this, LoginPage::class.java)
                intent.putExtra("serverAddress",serverAddress)
                startActivity(intent)
            }
        }
    }



}