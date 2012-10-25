package org.opencv.samples.tutorial1;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;
import java.net.UnknownHostException;
import java.security.PublicKey;
import java.util.ArrayList;

import org.opencv.android.BaseLoaderCallback;
import org.opencv.android.LoaderCallbackInterface;
import org.opencv.android.OpenCVLoader;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.os.Bundle;
import android.os.Environment;
import android.speech.RecognizerIntent;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.Window;
import android.view.WindowManager;

public class Sample1Java extends Activity {
    private static final String TAG = "OCVSample::Activity";

	private static final int VR_REQUEST = 987;

    private MenuItem            mItemPreviewRGBA;
    private MenuItem            mItemPreviewHSV;
    private MenuItem            mItemPreviewBall;
    private MenuItem			mItemCommand;
    private Sample1View         mView;



    private BaseLoaderCallback  mOpenCVCallBack = new BaseLoaderCallback(this) {
        @Override
        public void onManagerConnected(int status) {
            switch (status) {
                case LoaderCallbackInterface.SUCCESS:
                {
                    Log.i(TAG, "OpenCV loaded successfully");
                    // Create and set View
                    mView = new Sample1View(mAppContext);
                    setContentView(mView);
                    
                   
                    File objfile = getFileStreamPath("objectname.txt");
                    if(objfile.exists()){
                    	 String objstring = "" ;
                         try {
                             FileInputStream fIn = openFileInput ( "objectname.txt" ) ;
                             InputStreamReader isr = new InputStreamReader ( fIn ) ;
                             BufferedReader buffreader = new BufferedReader ( isr ) ;

                             String readString = buffreader.readLine ( ) ;
                             while ( readString != null ) {
                            	 objstring= objstring + readString ;
                                 readString = buffreader.readLine ( ) ;
                             }
                             
                             isr.close ( ) ;
                             mView.setOverlayText(objstring);
                         	
                         } catch ( IOException ioe ) {
                             ioe.printStackTrace ( ) ;
                             mView.setOverlayText(objstring);
                         	
                         }
                        
                    }else{
                    	  try {
                              FileOutputStream fOut = openFileOutput ( "objectname.txt" , MODE_WORLD_READABLE ) ;
                              OutputStreamWriter osw = new OutputStreamWriter ( fOut ) ;
                              osw.write ( "ball" ) ;
                              osw.flush ( ) ;
                              osw.close ( ) ;
                          } catch ( Exception e ) {
                              e.printStackTrace ( ) ;
                          }
                    	  mView.setOverlayText("ball");
                    }
                    
                    
                    // Check native OpenCV camera
                    if( !mView.openCamera() ) {
                        AlertDialog ad = new AlertDialog.Builder(mAppContext).create();
                        ad.setCancelable(false); // This blocks the 'BACK' button
                        ad.setMessage("Fatal error: can't open camera!");
                        ad.setButton(AlertDialog.BUTTON_POSITIVE, "OK", new DialogInterface.OnClickListener() {
                            public void onClick(DialogInterface dialog, int which) {
                                dialog.dismiss();
                                finish();
                            }
                        });
                        ad.show();
                    }
                } break;

                /** OpenCV loader cannot start Google Play **/
                case LoaderCallbackInterface.MARKET_ERROR:
                {
                    Log.d(TAG, "Google Play service is not accessible!");
                    AlertDialog MarketErrorMessage = new AlertDialog.Builder(mAppContext).create();
                    MarketErrorMessage.setTitle("OpenCV Manager");
                    MarketErrorMessage.setMessage("Google Play service is not accessible!\nTry to install the 'OpenCV Manager' and the appropriate 'OpenCV binary pack' APKs from OpenCV SDK manually via 'adb install' command.");
                    MarketErrorMessage.setCancelable(false); // This blocks the 'BACK' button
                    MarketErrorMessage.setButton(AlertDialog.BUTTON_POSITIVE, "OK", new DialogInterface.OnClickListener() {
                        public void onClick(DialogInterface dialog, int which) {
                            finish();
                        }
                    });
                    MarketErrorMessage.show();
                } break;
                default:
                {
                    super.onManagerConnected(status);
                } break;
            }
        }
    };

    public Sample1Java() {
        Log.i(TAG, "Instantiated new " + this.getClass());
    }

    @Override
    protected void onPause() {
        Log.i(TAG, "called onPause");
        if (null != mView)
            mView.releaseCamera();
        super.onPause();
    }

    @Override
    protected void onResume() {
        Log.i(TAG, "called onResume");
        super.onResume();

        Log.i(TAG, "Trying to load OpenCV library");
        if (!OpenCVLoader.initAsync(OpenCVLoader.OPENCV_VERSION_2_4_2, this, mOpenCVCallBack)) {
            Log.e(TAG, "Cannot connect to OpenCV Manager");
        }
    }

    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState) {
        Log.i(TAG, "called onCreate");
        super.onCreate(savedInstanceState);
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        Log.i(TAG, "called onCreateOptionsMenu");
        mItemPreviewRGBA = menu.add("Preview RGBA");
        mItemPreviewHSV = menu.add("Preview HSV");
        mItemPreviewBall = menu.add("Object");
        mItemCommand = menu.add("Command");
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        Log.i(TAG, "called onOptionsItemSelected; selected item: " + item);
        if (item == mItemPreviewRGBA) {
            mView.setViewMode(Sample1View.VIEW_MODE_RGBA);
        } else if (item == mItemPreviewHSV) {
            mView.setViewMode(Sample1View.VIEW_MODE_HSV);
        } else if (item == mItemPreviewBall) {
        	mView.setViewMode(Sample1View.VIEW_MODE_BALL);
        }else if(item == mItemCommand){
        	listenToSpeech();
        }
        return true;
    }
    
    private void listenToSpeech() {
        //start the speech recognition intent passing required data
        Intent listenIntent = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
        //indicate package
        listenIntent.putExtra(RecognizerIntent.EXTRA_CALLING_PACKAGE, getClass().getPackage().getName());
        //message to display while listening
        listenIntent.putExtra(RecognizerIntent.EXTRA_PROMPT, "Say a word!");
        //set speech model
        listenIntent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
        //specify number of results to retrieve
        listenIntent.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 10);
        //start listening
        startActivityForResult(listenIntent, VR_REQUEST);
    }
    

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        //check speech recognition result
        if (requestCode == VR_REQUEST && resultCode == RESULT_OK)
        {
            //store the returned word list as an ArrayList
            ArrayList<String> suggestedWords = data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS);
            if (suggestedWords != null)
            {
            	String firstResult = suggestedWords.get(0);
            	mView.setOverlayText(firstResult);
            	
            	File objfile = getFileStreamPath("objectname.txt");
                                	  try {
                          FileOutputStream fOut = openFileOutput ( "objectname.txt" , MODE_WORLD_READABLE ) ;
                          OutputStreamWriter osw = new OutputStreamWriter ( fOut ) ;
                          osw.write ( firstResult) ;
                          osw.flush ( ) ;
                          osw.close ( ) ;
                      } catch ( Exception e ) {
                          e.printStackTrace ( ) ;
                      }
               
            	
            }
            //set the retrieved list to display in the ListView using an ArrayAdapter
            }
      
        //call superclass method
        super.onActivityResult(requestCode, resultCode, data);
        
    }
   
    
}
