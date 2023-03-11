package hk.hku.fyp.camera_notification_system

import android.content.Intent
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.util.Log
import android.widget.*
import com.android.volley.Request
import com.android.volley.Response
import com.android.volley.toolbox.JsonObjectRequest
import com.android.volley.toolbox.Volley
import org.json.JSONArray
import org.json.JSONObject

class LoginPage : AppCompatActivity() {

    private var loginID: EditText? = null;
    private var loginPass: EditText? = null;
    private var loginButton:Button? = null;

    private var serverAddress: String? = null;

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login_page)


        loginButton = findViewById<Button>(R.id.login_button)
        loginID = findViewById<EditText>(R.id.login_id)
        loginPass = findViewById<EditText>(R.id.login_pass)

        serverAddress = intent.getStringExtra("serverAddress") as String

        loginButton!!.setOnClickListener {
            fetchLogin(
                loginID!!.text.toString(),
                loginPass!!.text.toString()
            )
        }
    }

    private fun fetchLogin(loginID:String, loginPass:String){
        val loginUrl = "$serverAddress/login?officer_id=$loginID&password=$loginPass"
        val jsonObjRequest = JsonObjectRequest(
            Request.Method.GET, loginUrl, null,
            Response.Listener { response -> returnLoginDetails(response)},
            Response.ErrorListener { error -> Log.e("RestDetails: ", error.toString()) }
        )
        Volley.newRequestQueue(this).add(jsonObjRequest)
    }

    private fun returnLoginDetails(jsonObj: JSONObject){
        val userToken = jsonObj.getString("api_token")
        val intent = Intent(this, MainActivity::class.java)
        intent.putExtra("userToken", userToken)
        startActivity(intent)
    }
}