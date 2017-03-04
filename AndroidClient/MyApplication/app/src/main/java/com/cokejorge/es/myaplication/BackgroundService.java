package com.cokejorge.es.myaplication;

        import android.Manifest;
        import android.app.NotificationManager;
        import android.app.PendingIntent;
        import android.app.Service;
        import android.content.BroadcastReceiver;
        import android.content.Context;
        import android.content.Intent;
        import android.content.pm.PackageManager;
        import android.location.Location;
        import android.location.LocationManager;
        import android.media.MediaPlayer;
        import android.os.Bundle;
        import android.os.IBinder;
        import android.os.Vibrator;
        import android.provider.Settings;
        import android.support.v4.app.ActivityCompat;
        import android.support.v4.app.NotificationCompat;

        import android.util.Log;
        import android.widget.Toast;

/**
 * Clase encargada de Gestionar el Servicio en Segundo Plano
 */
public class BackgroundService extends Service implements MediaPlayer.OnCompletionListener {

    private static final String TAG = "DEVELOP";
    private LocationManager mLocationManager = null;
    private static final String NOTIFICATION_DELETED_ACTION = "NOTIFICATION_DELETED";
    private LocationListener mLocationListener = new LocationListener(LocationManager.GPS_PROVIDER);

    Vibrator vibrator;

    int index = 0;
    MediaPlayer mp = new MediaPlayer();


    //A través de este objeto se recibe información de la notificacion
    private final BroadcastReceiver receiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            //Cuando recibimos info en la notificación (es decir, descartamos la notificacion), terminamos el service
            terminarService();
            unregisterReceiver(this);
        }
    };


    //Metodo necesario para extender la clase Service
    @Override
    public IBinder onBind(Intent arg0) {
        Log.e(TAG, "onBind - SERVICE");
        return null;
    }

    /**
     * Metodo lanzado al terminar la ejecución de onCreate
     * Metodo encargado de obtener la URI pasada al intent desde la Actividad Principal, iniciar una conexión rest a través
     * del metodo ConnectionImplementator.init(uri), y mostrar la notificación al usuario.
     * @param intent
     * @param flags
     * @param startId
     * @return
     */
    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        Log.e(TAG, "onStartCommand - SERVICE");
        //String value = intent.getExtras().getString("uri");

        //Mostramos notificacion
        sendNotification(this);
        super.onStartCommand(intent, flags, startId);
        return START_STICKY;
    }

    /**
     * Metodo encargado de terminar el servicio (this)
     */

    public void terminarService(){
        this.stopSelf();
    }


    /**
     * Metodo encargado de mostrar una notifiación al usuario. En caso de que ya exista, la elimina y muestra una nueva.
     * @param context
     */
    public void sendNotification(Context context) {

        NotificationManager mNotificationManager = (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);

        Intent intent = new Intent(context, AlertActivity.class);
        PendingIntent pendingIntent = PendingIntent.getActivity(getApplicationContext(), 0, intent, Intent.FILL_IN_ACTION);

        NotificationCompat.Action action =
                new NotificationCompat.Action.Builder(android.R.drawable.ic_menu_send,
                        "ALERTA", pendingIntent)
                        .build();
        Intent intentDelete = new Intent(NOTIFICATION_DELETED_ACTION);
        PendingIntent pendintIntent = PendingIntent.getBroadcast(context, 0, intentDelete, 0);

        NotificationCompat.Builder mBuilder =
                new NotificationCompat.Builder(context)
                        .setSmallIcon(android.R.drawable.ic_menu_mylocation)
                        .setContentTitle("Monitorizacion")
                        .setContentText("Monitorizando localizacion en segundo plano...")
                        .setAutoCancel(true)
                        .setSound(Settings.System.DEFAULT_NOTIFICATION_URI)
                        .setDeleteIntent(pendintIntent)
                        .addAction(action);
        mBuilder.setContentIntent(pendingIntent);
        //Notificacion TAG-KEY -> Geome-0
        mNotificationManager.notify("Geome", 0, mBuilder.build());
        Toast.makeText(getApplicationContext(), "Descarte la notifiación para terminar con la monitorización en segundo plano.", Toast.LENGTH_LONG).show();
    }

    /**
     * Metodo ejecutado al iniciar el Service.
     * Inicializamos el mLocationManager y lo configuramo para recibir actualizaciones cada 3 segundos
     */
    @Override
    public void onCreate() {
        Log.e(TAG, "onCreate - SERVICE");
        vibrator = (Vibrator)getSystemService(Context.VIBRATOR_SERVICE);
        if (mLocationManager == null) {
            mLocationManager = (LocationManager) getApplicationContext().getSystemService(Context.LOCATION_SERVICE);
        }
        try {
            mLocationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER, 3000, 0, mLocationListener);
        } catch (java.lang.SecurityException ex) {
            Log.i(TAG, "fail to request location update, ignore", ex);
        } catch (IllegalArgumentException ex) {
            Log.d(TAG, "network provider does not exist, " + ex.getMessage());
        }
    }

    /**
     * Metodo ejecutado al terminar el Service
     * Eliminamos el listener de mLocationManager y borramos el usuario creado en la BD
     */
    @Override
    public void onDestroy() {
        Log.e(TAG, "onDestroy - SERVICE");
        super.onDestroy();
        if (mLocationManager != null) {
            try {
                if (ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED && ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
                    return;
                }
                mLocationManager.removeUpdates(mLocationListener);
            } catch (Exception ex) {
                Log.i(TAG, "fail to remove location listners, ignore", ex);
            }
        }
    }

    /**
     * Clase encargada de implementar el LocationListener
     */
    //TODO IMPORTANTE: Mover Logica de LocationListener a clase a parte, es común entre el Servicio en segundo Plano y la Actividad Principal
    private class LocationListener implements android.location.LocationListener  {
        Location mLastLocation; //Guardamos la ultima localizacion

        public LocationListener(String provider) {
            Log.e(TAG, "LocationListener " + provider);
            mLastLocation = new Location(provider);
        }

        @Override
        public void onLocationChanged(Location location) {
            Log.e(TAG, "onLocationChanged: " + location);
            mLastLocation = location;
        }

        @Override
        public void onProviderDisabled(String provider) {
            Log.e(TAG, "onProviderDisabled: " + provider);
            Toast.makeText(getApplicationContext(), "[GeoME] GeoME no podrá monitorizar su ubicación sin activar la Localización GPS.", Toast.LENGTH_SHORT).show();
        }

        @Override
        public void onProviderEnabled(String provider) {
            Toast.makeText(getApplicationContext(), "[GeoME] Reanudando monitorización.", Toast.LENGTH_SHORT).show();
            Log.e(TAG, "onProviderEnabled: " + provider);
        }

        @Override
        public void onStatusChanged(String provider, int status, Bundle extras) {
            Log.e(TAG, "onStatusChanged: " + provider);
        }

    }


    //TODO: IMPORTANTE, MOVER LA LOGICA DE ALERTAS, EN EL FUTURO PUEDE COMPLICARSE (CÁLCULO DE DISTANCIAS, ORIENTACION...), ademas es común entre el Servicio en segundo Plano y la Actividad Principal
    @Override
    public void onCompletion(MediaPlayer mp) {
        index++;
        play();
    }
    private void play() {
        /*
            try {
                Log.e(TAG, "Se hace un play() dentro del try" + Integer.toString(listaCanciones.get(index)));
                AssetFileDescriptor afd = getResources().openRawResourceFd(listaCanciones.get(index));
                mp.reset();
                mp.setDataSource(afd.getFileDescriptor(), afd.getStartOffset(), afd.getDeclaredLength());
                mp.prepare();
                mp.start();
                afd.close();
            } catch (IllegalArgumentException e) {
                Log.e(TAG, "Error audio: " + e.getMessage(), e);
            } catch (IllegalStateException e) {
                Log.e(TAG, "Error audio: " + e.getMessage(), e);
            } catch (IOException e) {
                Log.e(TAG, "Error audio: " + e.getMessage(), e);
            }
            */
    }
    public void alertaLogic(int vAntes, int bAntes, int pAntes) {
        /*
        index = 0;

        if (mp != null && mp.isPlaying()) {
            mp.stop();
        }
        mp = MediaPlayer.create(this,listaCanciones.get(0));
        mp.setOnCompletionListener(this);
        mp.start();
        */
    }

}
