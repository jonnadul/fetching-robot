package org.opencv.samples.tutorial1;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import org.opencv.android.Utils;
import org.opencv.core.Core;
import org.opencv.core.CvType;
import org.opencv.core.Mat;
import org.opencv.core.MatOfPoint;
import org.opencv.core.Point;
import org.opencv.core.Scalar;
import org.opencv.core.Size;
import org.opencv.imgproc.Imgproc;

import android.content.Context;
import android.graphics.Bitmap;
import android.os.Environment;
import android.util.Log;

class Sample1View extends SampleViewBase {
    private static final String TAG = "OCVSample::View";

    public static final int     VIEW_MODE_RGBA  = 0;
    public static final int     VIEW_MODE_HSV  = 1;
    public static final int     VIEW_MODE_BALL = 2;

    private String 				mOverlayText = "OPENCV";
  

	private Mat                 mYuv;
    private Mat                 mRgba;
    private Mat					mHsv;
    private Mat					mThreshMat;
    private Mat                 mGraySubmat;
    private Mat                 mIntermediateMat;
    private Bitmap              mBitmap;
    private int                 mViewMode;

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
        mRgba = new Mat();
        mIntermediateMat = new Mat();

        mBitmap = Bitmap.createBitmap(previewWidth, previewHeight, Bitmap.Config.ARGB_8888);
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
        }
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
        	 Core.inRange(mHsv, new Scalar(30,30,30), new Scalar(100,255,255), mThreshMat);
        	 Imgproc.erode(mThreshMat, mThreshMat,  Imgproc.getStructuringElement(Imgproc.MORPH_RECT, new Size(7,7)));
        	 Imgproc.dilate(mThreshMat, mThreshMat,  Imgproc.getStructuringElement(Imgproc.MORPH_RECT, new Size(7,7)));
        	 //Imgproc.cvtColor(mThreshMat, mHsv, Imgproc.COLOR_GRAY2RGB);
        	 //Imgproc.cvtColor(mHsv, mRgba, Imgproc.COLOR_RGB2RGBA);
        	List<MatOfPoint> contours = new ArrayList<MatOfPoint>();
        	
        	 Mat hierarchy = new Mat(mRgba.size(),CvType.CV_8UC1, new Scalar(0));
        	 Imgproc.findContours(mThreshMat, contours, hierarchy,Imgproc.RETR_EXTERNAL, Imgproc.CHAIN_APPROX_SIMPLE);

        	 
        	// Find max contour area
             double areaMax = 0;
             double areaCalc;
             Iterator<MatOfPoint> contIter = contours.iterator();
             MatOfPoint contMat;
             MatOfPoint maxMat = null;
             int iterIndex = 0;
             int maxIndex = -1;
             int minArea = 300;
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
        		 Iterator<Point> pointIter;
        		 Imgproc.drawContours(mRgba, contours,maxIndex, new Scalar(255,0,0));
        		 pointIter = maxMat.toList().iterator();
        		 Point ballPoint;
        		 int minX = Integer.MAX_VALUE;
        		 int minY = Integer.MAX_VALUE;
        		 int maxX = 0;
        		 int maxY = 0;
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
        	 }
        	 /*if (mCascade != null) {
                 int heightG = mGraySubmat.rows();
                 int faceSize = Math.round(heightG * minFaceSize);
                 faces = new MatOfRect();
                 mCascade.detectMultiScale(mGraySubmat, faces, 1.1, 2, 2 
                         , new Size(faceSize, faceSize), new Size());
                 Rect[] facesArray = faces.toArray();
                 for (int i = 0; i < facesArray.length; i++)
                     Core.rectangle(mRgba, facesArray[i].tl(), facesArray[i].br(), new Scalar(0, 255, 0, 255), 3);
                 //out.setData(("Frame").getBytes());
                 //try {
				//	socket.send(out);
				//} catch (IOException e) {
				//	// TODO Auto-generated catch block
				//	e.printStackTrace();
				//}
          	 }*/
        	//Imgproc.cvtColor(mGraySubmat, mRgba, Imgproc.COLOR_GRAY2RGBA, 4);
        	//Core.rectangle(mRgba, new Point(10,10), new Point(100, 100), new Scalar(0, 255, 0, 255), 3);
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
}
