package org.opencv.samples.tutorial1;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;
import java.net.UnknownHostException;
import java.nio.ByteBuffer;
import java.nio.IntBuffer;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import org.opencv.android.Utils;
import org.opencv.core.Core;
import org.opencv.core.CvType;
import org.opencv.core.Mat;
import org.opencv.core.MatOfPoint;
import org.opencv.core.Point;
import org.opencv.core.Rect;
import org.opencv.core.Scalar;
import org.opencv.core.Size;
import org.opencv.imgproc.Imgproc;

import android.content.Context;
import android.graphics.Bitmap;
import android.util.Log;

class Sample1View extends SampleViewBase {
    private static final String TAG = "OCVSample::View";

    /* Image view modes */
    public static final int     VIEW_MODE_RGBA  = 0;
    public static final int     VIEW_MODE_HSV  = 1;
    public static final int     VIEW_MODE_BALL = 2;
    public static final int		VIEW_MODE_PYR = 3;
    public static final int		VIEW_MODE_SAMPLE = 4;
    
    /* Color modes : Which color to find */
    public static final int		COLOR_MODE_R = 0;
    public static final int		COLOR_MODE_G = 1;
    public static final int		COLOR_MODE_B = 2;
    public static final int		COLOR_MODE_Y = 3;
    public static final int		COLOR_MODE_M = 4;
    public static final int		COLOR_MODE_O = 5;
    
    /* Robot Modes : Track or Pickup or Idle */
    public static final int 	ROBOT_MODE_STOP = 0;
    public static final int		ROBOT_MODE_TRACK = 1;
    public static final int		ROBOT_MODE_FETCH = 2;
    public static final int		ROBOT_MODE_WALL = 3;
    
    private String 				mOverlayText = "OPENCV";
  
    /* Image matricies for image processing */
	private Mat                 mYuv;
    private Mat                 mRgba;
    private Mat					mHsv;
    private Mat					mThreshMat;
    private Mat					mThreshMata;
    private Mat					mThreshMatb;
    private Mat                 mGraySubmat;
    private Mat                 mIntermediateMat;
    private Bitmap              mBitmap;
    
    /* View mode, color mode, robot mode */
    private int                 mViewMode;
    private int					mColorMode;
    private int					mRobotMode;

	private Scalar 				mThreshLow = new Scalar(38,40,10);
    private Scalar				mThreshHigh = new Scalar(80,255,255);

    /* HSV low and high thresholds for different colors */
    /*Yellow*/
    private Scalar yLow = new Scalar(25,40,100);
	private Scalar yHi = new Scalar(50,255,255);
	
	/*Green*/
	private Scalar gLow = new Scalar(70,60,40); //was 70,40,40
	private Scalar gHi = new Scalar(120,255,255);
	
	/*Red (low portion of H spectrum) */
	private Scalar rLowA = new Scalar(0,40,70);
	private Scalar rHiA = new Scalar(20,255,255);
	
	/*Red (high portion of H spectrum) */
	private Scalar rLowB = new Scalar(220,40,70);
	private Scalar rHiB = new Scalar(255,255,255);
	
	/*Blue*/
	private Scalar bLow = new Scalar(135,30,30);
	private Scalar bHi = new Scalar(170,255,255);
    
	/*Variables for UDP stream */
	protected DatagramSocket socket;
	protected byte[] outData;
	protected InetAddress serverIP;
	protected DatagramPacket out;

	/* Variables for figuring out contour size and area */
	private List<MatOfPoint> contours;
	private Mat hierarchy;
	private double areaMax;
	private double areaCalc;
	private Iterator<MatOfPoint> contIter;
	private MatOfPoint contMat;
	private MatOfPoint maxMat;
	private int iterIndex;
	private int maxIndex;
	private int minArea;
	private Iterator<Point> pointIter;
	private Point ballPoint;

	/* Variables for calculating minimum x,y coords in contours */
	private int minX;
	private int minY;
	private int maxX;
	private int maxY;
    
    public Sample1View(Context context) {
        super(context);
        mViewMode = VIEW_MODE_RGBA;
        Log.i(TAG, "Instantiated new " + this.getClass());
        
        
    }

    @Override
    protected void onPreviewStarted(int previewWidth, int previewHeight) {
        Log.i(TAG, "called onPreviewStarted("+previewWidth+", "+previewHeight+")");

        // initialize Mats before usage
        mYuv = new Mat(getFrameHeight() + getFrameHeight() / 2, getFrameWidth(), CvType.CV_8UC1);
        mGraySubmat = mYuv.submat(0, getFrameHeight(), 0, getFrameWidth());
        mHsv = new Mat();
        mThreshMat = new Mat();
        mThreshMata = new Mat();
        mThreshMatb = new Mat();
        mRgba = new Mat();
        mIntermediateMat = new Mat();

        mBitmap = Bitmap.createBitmap(previewWidth, previewHeight, Bitmap.Config.ARGB_8888);
        
        try {
			socket = new DatagramSocket();
			outData =  ("Ping").getBytes();
			serverIP = InetAddress.getByName("192.168.2.106");
			out = new DatagramPacket(outData,outData.length, serverIP,54259);
			//Log.i(TAG, "Datagram sent");
			//socket.send(out);
	        
        } catch (UnknownHostException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}
		catch (SocketException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		} catch (IOException e) {
		// 	TODO Auto-generated catch block
			e.printStackTrace();
		}
        
    }

    @Override
    protected void onPreviewStopped() {
        Log.i(TAG, "called onPreviewStopped");

        if(mBitmap != null) {
            mBitmap.recycle();
            mBitmap = null;
        }

        synchronized (this) {
            // Explicitly deallocate Mats
            if (mYuv != null)
                mYuv.release();
            if (mRgba != null)
                mRgba.release();
            if (mHsv != null)
            	mHsv.release();
            if(mThreshMat!=null)
            	mThreshMat.release();
            if(mThreshMata!=null)
            	mThreshMata.release();
            if(mThreshMatb!=null)
            	mThreshMatb.release();
            if (mGraySubmat != null)
                mGraySubmat.release();
            if (mIntermediateMat != null)
                mIntermediateMat.release();

            mYuv = null;
            mRgba = null;
            mGraySubmat = null;
            mIntermediateMat = null;
            mHsv = null;
            mThreshMat = null;
            mThreshMata = null;
            mThreshMatb = null;
        }
    }

	private Scalar converScalarHsv2Rgba(Scalar hsvColor)
	{	
        Mat pointMatRgba = new Mat();
        Mat pointMatHsv = new Mat(1, 1, CvType.CV_8UC3, hsvColor);
        Imgproc.cvtColor(pointMatHsv, pointMatRgba, Imgproc.COLOR_HSV2RGB_FULL, 4);
        
        return new Scalar(pointMatRgba.get(0, 0));
	}
    
    @Override
    protected Bitmap processFrame(byte[] data) {
        mYuv.put(0, 0, data);

        final int viewMode = mViewMode;

        switch (viewMode) {
        case VIEW_MODE_HSV:
        	 Imgproc.cvtColor(mYuv, mGraySubmat, Imgproc.COLOR_YUV420sp2RGB, 4);
             Imgproc.cvtColor(mGraySubmat, mRgba, Imgproc.COLOR_RGB2HSV,0);
            break;
        case VIEW_MODE_RGBA:
            Imgproc.cvtColor(mYuv, mRgba, Imgproc.COLOR_YUV420sp2RGB, 4);
			Core.putText(mRgba, mOverlayText, new Point(10, 100), 3/* CV_FONT_HERSHEY_COMPLEX */, 2, new Scalar(255, 0, 0, 255), 3);
            break;
        case VIEW_MODE_BALL:
        	 Imgproc.cvtColor(mYuv, mRgba, Imgproc.COLOR_YUV420sp2RGB, 4);
        	 Imgproc.cvtColor(mRgba, mHsv, Imgproc.COLOR_RGB2HSV,0);
        	 //Core.inRange(mHsv, new Scalar(38,40,10), new Scalar(80,255,255), mThreshMat);
        	 
        	 switch(mColorMode){
	        	 case COLOR_MODE_R:
	        		 Core.inRange(mHsv, rLowA, rHiA, mThreshMata);
	        		 Core.inRange(mHsv, rLowB, rHiB, mThreshMatb);
	        		 Core.bitwise_or(mThreshMata, mThreshMatb, mThreshMat);
	        		 break;
	        	default:
	        		mThreshLow = yLow;
	        		mThreshHigh = yHi;
	        		Core.inRange(mHsv, mThreshLow, mThreshHigh, mThreshMat);
	        		break; 
        	 }
        	 Core.rectangle(mRgba, new Point(344, 0), new Point(344, 20),new Scalar(255, 255, 0), 3); 
    		 
        	 Imgproc.erode(mThreshMat, mThreshMat,  Imgproc.getStructuringElement(Imgproc.MORPH_RECT, new Size(7,7)));
        	 Imgproc.dilate(mThreshMat, mThreshMat,  Imgproc.getStructuringElement(Imgproc.MORPH_RECT, new Size(7,7)));
        	 contours = new ArrayList<MatOfPoint>();
        	
        	 hierarchy = new Mat(mRgba.size(),CvType.CV_8UC1, new Scalar(0));
        	 Imgproc.findContours(mThreshMat, contours, hierarchy,Imgproc.RETR_EXTERNAL, Imgproc.CHAIN_APPROX_SIMPLE);

        	 
        	areaMax = 0;
             contIter = contours.iterator();
             maxMat = null;
             iterIndex = 0;
             maxIndex = -1;
             minArea = 300;
             while (contIter.hasNext()){
             	contMat = contIter.next();
             	areaCalc = Imgproc.contourArea(contMat);
             	if (areaCalc > minArea && areaCalc > areaMax){
             		areaMax = areaCalc;
             		maxMat = contMat;
             		maxIndex = iterIndex;
                }
             	iterIndex++;
             }
                       
        	 if(maxIndex >= 0){
        		 Imgproc.drawContours(mRgba, contours,maxIndex, new Scalar(255,0,0));
        		 pointIter = maxMat.toList().iterator();
        		 minX = Integer.MAX_VALUE;
        		 minY = Integer.MAX_VALUE;
        		 maxX = 0;
        		 maxY = 0;
        		 while(pointIter.hasNext())
        		 {
        			 ballPoint = pointIter.next();
        			 if(ballPoint.x > maxX){
        				 maxX = (int) Math.round(ballPoint.x);
        			 }else if(ballPoint.x < minX){
        				 minX = (int) Math.round(ballPoint.x);
        			 }
        			 
        			 if(ballPoint.y > maxY){
        				 maxY = (int)Math.round(ballPoint.y);
        			 }else if(ballPoint.y < minY){
        				 minY = (int)Math.round(ballPoint.y);
        			 }
        			 
        			 
        		 }
        		 Core.rectangle(mRgba, new Point(minX, minY), new Point(maxX, maxY),new Scalar(0, 0, 255), 3); 
        		 sendPointsUDP(minX, minY, maxX, maxY);
        	 }else{
        		 //no max point
        		sendPointsUDP(-9999,-9999,-9999,-9999);
        	 }
        	break;
        case VIEW_MODE_PYR:
        	Mat pyrDownMat = new Mat();
        	Imgproc.cvtColor(mYuv, mRgba, Imgproc.COLOR_YUV420sp2RGB, 4);

        	//Imgproc.pyrDown(mRgba, pyrDownMat);
        	//Imgproc.pyrDown(pyrDownMat, pyrDownMat);
        	Imgproc.cvtColor(mRgba, mHsv, Imgproc.COLOR_RGB2HSV_FULL);
        	Core.rectangle(mRgba, new Point(344, 0), new Point(344, 20),new Scalar(255, 255, 0), 3); 
   		 
       	 switch(mColorMode){
	    	 case COLOR_MODE_R:
	    		 Core.inRange(mHsv, rLowA, rHiA, mThreshMata);
        		 Core.inRange(mHsv, rLowB, rHiB, mThreshMatb);
        		 Core.bitwise_or(mThreshMata, mThreshMatb, mThreshMat);
        		 break;
	    	 case COLOR_MODE_G:
	    		Core.inRange(mHsv, gLow, gHi, mThreshMat);
	    		break;
	    	 case COLOR_MODE_B:
	    		Core.inRange(mHsv, bLow, bHi, mThreshMat);
		    	break;
	    	 case COLOR_MODE_M:  
	    	 case COLOR_MODE_O: 
	    	 case COLOR_MODE_Y:
	    	 default:
		    	Core.inRange(mHsv, yLow, yHi, mThreshMat);
	    		break; 
		 }
        	
       	 	Imgproc.dilate(mThreshMat, mThreshMat, new Mat());
       	 	
	       	//Mat pyrUpMat = new Mat();
	     	//Imgproc.pyrUp(mThreshMat, pyrUpMat);
	     	//Imgproc.pyrUp(pyrUpMat, pyrUpMat);
     	
       	 	//Imgproc.cvtColor(pyrUpMat, mHsv, Imgproc.COLOR_GRAY2RGB);
       	 	
       	 contours = new ArrayList<MatOfPoint>();
     	
    	 hierarchy = new Mat(mRgba.size(),CvType.CV_8UC1, new Scalar(0));
    	 Imgproc.findContours(mThreshMat, contours, hierarchy,Imgproc.RETR_EXTERNAL, Imgproc.CHAIN_APPROX_SIMPLE);

    	 
    	areaMax = 0;
         contIter = contours.iterator();
         maxMat = null;
         iterIndex = 0;
         maxIndex = -1;
         minArea = 300;
         while (contIter.hasNext()){
         	contMat = contIter.next();
         	areaCalc = Imgproc.contourArea(contMat);
         	if (areaCalc > minArea && areaCalc > areaMax){
         		areaMax = areaCalc;
         		maxMat = contMat;
         		maxIndex = iterIndex;
            }
         	iterIndex++;
         }
                   
    	 if(maxIndex >= 0){
    		 Imgproc.drawContours(mRgba, contours,maxIndex, new Scalar(255,0,0));
    		 pointIter = maxMat.toList().iterator();
    		 minX = Integer.MAX_VALUE;
    		 minY = Integer.MAX_VALUE;
    		 maxX = 0;
    		 maxY = 0;
    		 while(pointIter.hasNext())
    		 {
    			 ballPoint = pointIter.next();
    			 if(ballPoint.x > maxX){
    				 maxX = (int) Math.round(ballPoint.x);
    			 }else if(ballPoint.x < minX){
    				 minX = (int) Math.round(ballPoint.x);
    			 }
    			 
    			 if(ballPoint.y > maxY){
    				 maxY = (int)Math.round(ballPoint.y);
    			 }else if(ballPoint.y < minY){
    				 minY = (int)Math.round(ballPoint.y);
    			 }
    			 
    			 
    		 }
    		 Core.rectangle(mRgba, new Point(minX, minY), new Point(maxX, maxY),new Scalar(0, 0, 255), 3); 
    		 sendPointsUDP(minX, minY, maxX, maxY);
    	 }else{
    		 //no max point
    		sendPointsUDP(-9999,-9999,-9999,-9999);
    	 }
       	 	
       	 	/*
       	 	Imgproc.cvtColor(mHsv, mRgba, Imgproc.COLOR_RGB2RGBA);
       	 	*/
       	 	
       	 	
        	break;
        case VIEW_MODE_SAMPLE:
        	Rect touchedRect = new Rect();
 	        
 	        touchedRect.x = mRgba.cols()/2-4;
 	        touchedRect.y = mRgba.rows()/2-4;

 	        touchedRect.width = 8;
 	        touchedRect.height = 8;
 	        	
 	        Mat touchedRegionRgba = mRgba.submat(touchedRect);
 	        
 	        Mat touchedRegionHsv = new Mat();
 	        Imgproc.cvtColor(touchedRegionRgba, touchedRegionHsv, Imgproc.COLOR_RGB2HSV_FULL);
 	        
 	        // Calculate average color of touched region
 	        Scalar mBlobColorHsv = Core.sumElems(touchedRegionHsv);
 	        int pointCount = touchedRect.width*touchedRect.height;
 	        for (int i = 0; i < mBlobColorHsv.val.length; i++)
 	        {
 	        	mBlobColorHsv.val[i] /= pointCount;
 	        }
 	        
 	        //Scalar mBlobColorRgba = converScalarHsv2Rgba(mBlobColorHsv);
 	       mOverlayText = "(" + (int)mBlobColorHsv.val[0] + ", " + (int)mBlobColorHsv.val[1] + 
	    			", " + (int)mBlobColorHsv.val[2] + ")";
 	        Log.i(TAG, "Touched hsv color: "+ mOverlayText);
 	        
 	        mViewMode = VIEW_MODE_RGBA;
        	break;
        }

        Bitmap bmp = mBitmap;

        try {
            Utils.matToBitmap(mRgba, bmp);
        } catch(Exception e) {
            Log.e("org.opencv.samples.tutorial1", "Utils.matToBitmap() throws an exception: " + e.getMessage());
            bmp.recycle();
            bmp = null;
        }
        return bmp;
    }

    public void setViewMode(int viewMode) {
        Log.i(TAG, "called setViewMode("+viewMode+")");
        mViewMode = viewMode;
    }
    public void setOverlayText(String mOverlayText) {
  		this.mOverlayText = mOverlayText;
  	}
    
    protected int sendPointsUDP(int minX, int minY, int maxX, int maxY)
    {
    	 ByteBuffer byteBuffer = ByteBuffer.allocate(20);        
         IntBuffer intBuffer = byteBuffer.asIntBuffer();
         intBuffer.put(minX);
         intBuffer.put(minY);
         intBuffer.put(maxX);
         intBuffer.put(maxY);
         intBuffer.put(mRobotMode);
         
         byte[] array = byteBuffer.array();
    	
    	out.setData(array);
    	  try {
				socket.send(out);
				return 1;
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
    	  return 0;
    }

	public Scalar getThreshLow() {
		return mThreshLow;
	}

	public void setThreshLow(Scalar mThreshLow) {
		this.mThreshLow = mThreshLow;
	}

	public Scalar getThreshHigh() {
		return mThreshHigh;
	}

	public void setThreshHigh(Scalar mThreshHigh) {
		this.mThreshHigh = mThreshHigh;
	}

	public int getColorMode() {
		return mColorMode;
	}

	public void setColorMode(int mColorMode) {
		this.mColorMode = mColorMode;
	}
	

    public int getRobotMode() {
		return mRobotMode;
	}

	public void setRobotMode(int mRobotMode) {
		this.mRobotMode = mRobotMode;
	}
}
