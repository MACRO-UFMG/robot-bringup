//=====================================================EKF-Fast-LIO2=====================================================================
//Institutions: Federal University of Minas Gerais (UFMG), Federal University of Ouro Preto (UFOP) and Instituto Tecnológico Vale (ITV)
//Description: This file is responsible for merging the wheel odometry with the IMU data and the Fast-LIO2 odometry.
//Milestones: 
//
//             Date: September 22, 2025
//             Description: New version of the code including visual odometry measurement.
//             Members: Gilmar Pereira da Cruz Júnior and Gabriel Malaquias
//             E-mails: gilmarpcruzjunior@gmail.com, gmdeoliveira@ymail.com
//=======================================================================================================================================

#include "settings_adaptive_filter.h"

using namespace Eigen;
using namespace std;

//-----------------------------
// Adaptive EKF class
//-----------------------------
class AdaptiveOdomFilter{

private:
    // Measure
    Eigen::VectorXd _imuMeasure, _wheelMeasure, _lidarMeasure, _lidarMeasureL, _visualMeasure, _visualMeasureL;

    // Measure Covariance
    Eigen::MatrixXd _E_imu, _E_wheel, _E_lidar, _E_lidarL, _E_visual, _E_visualL, _E_pred;

    // States and covariances
    Eigen::VectorXd _X, _V;
    Eigen::MatrixXd _P, _PV;

    // pose and velocities
    Eigen::VectorXd _pose, _velocities;

    // Times
    double _imu_dt;
    double _wheel_dt;
    double _lidar_dt;
    double _visual_dt;

    // number of state or measure vectors
    int _N_STATES = 12;
    int _N_IMU = 9; 
    int _N_WHEEL = 2; 
    int _N_LIDAR = 6;
    int _N_VISUAL = 6;
    
    // boolean
    bool _imuActivated;
    bool _wheelActivated;
    bool _lidarActivated;
    bool _visualActivated;
    bool _imuNew;
    bool _wheelNew;
    bool _lidarNew;
    bool _visualNew;
    bool _velComp;
    bool _firstVisual;
    bool _firstLidar;
    bool _computing;

    // variáveis de controle
    bool _running = false;
    std::thread _thread;
    std::mutex _mutex;

    //------------------
    // Auxliar functions
    //------------------
    void allocateMemory();

    void initialization();

    void covariance_initialization();

    //-----------------
    // predict function
    //-----------------
    void prediction_stage(double dt);

    //-----------------
    // correction stage
    //-----------------
    void correction_wheel_stage(double dt);

    void correction_imu_stage(double dt);

    void correction_lidar_stage(double dt);

    void correction_visual_stage(double dt);

    //---------
    // Models
    //---------
    VectorXd f_prediction_model(VectorXd x, double dt);

    VectorXd indirect_odometry_measurement(VectorXd u, VectorXd ul, double dt, char type);

    //----------
    // Jacobians
    //----------
    MatrixXd jacobian_state(VectorXd x, double dt);

    MatrixXd jacobian_odometry_measurement(VectorXd u, VectorXd ul, double dt, char type);

    MatrixXd jacobian_odometry_measurementL(VectorXd u, VectorXd ul, double dt, char type);

    //----------------
    // run
    //----------------
    void run();

    //---------------------------
    // covariances functions
    //---------------------------
    MatrixXd adaptive_covariance(double fCorner, double fSurf);

    MatrixXd adaptive_visual_covariance(double IntensityIn);

    MatrixXd wheelOdometryAdaptiveCovariance(double omegaz_wheel_odom, double omegaz_imu);


public:
    //------------------
    // Filter settings
    //------------------
    bool enableImu;
    bool enableWheel;
    bool enableLidar;
    bool enableVisual;
    double freq;

    float alpha_lidar;
    float alpha_visual;

    //------------------
    // Covariance settings
    //------------------
    float lidarG;
    float visualG;
    float wheelG;
    float imuG;

    float gamma_vx;
    float gamma_omegaz;
    float delta_vx;
    float delta_omegaz;

    int lidar_type_func;
    int visual_type_func;
    int wheel_type_func;

    // adaptive covariance - lidar odometry
    double nCorner, nSurf; 
    double Gx, Gy, Gz, Gphi, Gtheta, Gpsi;
    double Gvx, Gvy, Gvz, Gvphi, Gvtheta, Gvpsi;
    float l_min;

    double minIntensity; 
    double maxIntensity; 

    //------------------
    // Constructor -  Destructor
    //------------------   
    AdaptiveOdomFilter();
    ~AdaptiveOdomFilter();
    
    //----------
    // Datas - ok
    //----------
    void correction_imu_data(VectorXd imu, MatrixXd E_imu, double dt);

    void correction_wheel_data(VectorXd wheel_odom, MatrixXd E_wheel, double dt, double omegaz_imu);

    void correction_lidar_data(VectorXd lidar_odom, MatrixXd E_lidar, double dt, double corner, double surf);

    void correction_visual_data(VectorXd visual_odom, MatrixXd E_visual, double dt, double averageIntensity);

    //------------------
    // filter control
    // -----------------
    void get_state(VectorXd &X_state, MatrixXd &E_state);

    void set_initial_state(VectorXd X_state, MatrixXd E_state);

    void start();     // inicia a thread

    void stop();      // para a thread

};
