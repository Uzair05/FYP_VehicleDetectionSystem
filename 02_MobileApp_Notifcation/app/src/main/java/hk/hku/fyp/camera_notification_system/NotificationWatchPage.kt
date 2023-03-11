package hk.hku.fyp.camera_notification_system

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button

class NotificationWatchPage : AppCompatActivity() {

    private var serverAddress: String? = null;

    private var userToken: String? = null;
    private var newAlertButton: Button? = null;
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_notification_watch_page)

        newAlertButton = findViewById<Button>(R.id.newAlert)
        newAlertButton!!.setOnClickListener{
            fetchData()
        }

        if (userToken == null){
            loginUser()
        }
    }
    private fun loginUser(){
        // get userToken from memory --> if not found then go to login activity
    }

    private fun fetchData(){
        // fetch latest data from web server
    }
}