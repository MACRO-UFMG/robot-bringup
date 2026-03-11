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

#include <adaptive_odom_filter/ekf_adaptive_tools.h>
// +++ ROS 2 addition (for rclcpp::Rate, rclcpp::Clock, rclcpp::ok) +++
#include <rclcpp/rclcpp.hpp>

using namespace Eigen;
using namespace std;

//------------------
// Constructor - Destructor
//------------------   
AdaptiveOdomFilter::AdaptiveOdomFilter(){
    // alocate memory
    allocateMemory();

    // initialization
    initialization();
    covariance_initialization();
}

AdaptiveOdomFilter::~AdaptiveOdomFilter() {
    stop();  
}

//**************************
// PRIVATE FUNCTIONS
//**************************
//------------------
// Auxliar functions
//------------------
void AdaptiveOdomFilter::allocateMemory(){
    _imuMeasure.resize(_N_IMU);
    _wheelMeasure.resize(_N_WHEEL);
    _lidarMeasure.resize(_N_LIDAR);
    _lidarMeasureL.resize(_N_LIDAR);
    _visualMeasure.resize(_N_VISUAL);
    _visualMeasureL.resize(_N_VISUAL);

    _E_imu.resize(_N_IMU,_N_IMU);
    _E_wheel.resize(_N_WHEEL,_N_WHEEL);
    _E_lidar.resize(_N_LIDAR,_N_LIDAR);
    _E_lidarL.resize(_N_LIDAR,_N_LIDAR);
    _E_visual.resize(_N_VISUAL,_N_VISUAL);
    _E_visualL.resize(_N_VISUAL,_N_VISUAL);
    _E_pred.resize(_N_STATES,_N_STATES);

    _X.resize(_N_STATES);
    _P.resize(_N_STATES,_N_STATES);

    _V.resize(_N_STATES);
    _PV.resize(_N_STATES,_N_STATES);
}

void AdaptiveOdomFilter::initialization(){
    // times and frequencies
    _imu_dt = 0.0005;
    _wheel_dt = 0.05;
    _lidar_dt = 0.1;
    _visual_dt = 0.005;

    freq = 200;

    // boolean
    _imuActivated = false;
    _lidarActivated = false;
    _wheelActivated = false;
    _visualActivated = false;
    _imuNew = false;
    _wheelNew = false;
    _lidarNew = false;
    _visualNew = false;    
    _firstVisual =  true;
    _firstLidar = true;  

    enableImu = false;
    enableWheel = false;
    enableLidar = false;
    enableVisual = false;

    _computing = false;

    // matrices and vectors
    _imuMeasure = Eigen::VectorXd::Zero(_N_IMU);
    _wheelMeasure = Eigen::VectorXd::Zero(_N_WHEEL);
    _lidarMeasure = Eigen::VectorXd::Zero(_N_LIDAR);
    _lidarMeasureL = Eigen::VectorXd::Zero(_N_LIDAR);
    _visualMeasure = Eigen::VectorXd::Zero(_N_VISUAL);
    _visualMeasureL = Eigen::VectorXd::Zero(_N_VISUAL);
    
    _E_imu = Eigen::MatrixXd::Zero(_N_IMU,_N_IMU);
    _E_lidar = Eigen::MatrixXd::Zero(_N_LIDAR,_N_LIDAR);
    _E_lidarL = Eigen::MatrixXd::Zero(_N_LIDAR,_N_LIDAR);
    _E_visual = Eigen::MatrixXd::Zero(_N_VISUAL,_N_VISUAL);
    _E_visualL = Eigen::MatrixXd::Zero(_N_VISUAL,_N_VISUAL);
    _E_wheel = Eigen::MatrixXd::Zero(_N_WHEEL,_N_WHEEL);
    _E_pred = Eigen::MatrixXd::Zero(_N_STATES,_N_STATES);

    // indirect measurement
    alpha_lidar = 1.0;
    alpha_visual = 0.999;

    // state initial
    _X = Eigen::VectorXd::Zero(_N_STATES);
    _P = Eigen::MatrixXd::Zero(_N_STATES,_N_STATES);
    _V = Eigen::VectorXd::Zero(_N_STATES);

    // covariance initial
    _P(0,0) = 0.1;   // x
    _P(1,1) = 0.1;   // y
    _P(2,2) = 0.1;   // z
    _P(3,3) = 0.1;   // roll
    _P(4,4) = 0.1;   // pitch
    _P(5,5) = 0.1;   // yaw
    _P(6,6) = 0.1;   // vx
    _P(7,7) = 0.1;   // vy
    _P(8,8) = 0.1;   // vz
    _P(9,9) = 0.1;   // wx
    _P(10,10) = 0.1;   // wy
    _P(11,11) = 0.1;   // wz

    // Fixed prediction covariance
    _E_pred.block(6,6,6,6) = 0.01*_P.block(6,6,6,6);

    // out data
    _V = _X;
    _PV = _P;

    // visual covariances variables
    minIntensity = 0.0; // only to teste
    maxIntensity = 1.0; // only to teste
}

void AdaptiveOdomFilter::covariance_initialization(){
    // parameters
    lidar_type_func = 0;
    visual_type_func = 0;
    wheel_type_func = 0;

    lidarG = 1.0;
    visualG = 1.0;
    wheelG = 1.0;
    imuG = 1.0;

    // adptive covariance constants - lidar odometry
    nCorner = 500.0; // 7000
    nSurf = 5000;    // 5400
    
    Gz = 0.0048;    // x [m]
    Gx = 0.0022;    // y [m]
    Gy = 0.0016;    // z [m]
    Gpsi = 0.0044;  // phi [rad]
    Gphi = 0.0052;  // theta [rad]
    Gtheta = 0.005; // psi [rad]

    Gvz = 0.001;    // x [m]
    Gvx = 0.001;    // y [m]
    Gvy = 0.001;    // z [m]
    Gvpsi = 0.001;  // phi [rad]
    Gvphi = 0.001;  // theta [rad]
    Gvtheta = 0.001; // psi [rad]

    l_min = 0.01;
}

//-----------------
// predict function
//-----------------
void AdaptiveOdomFilter::prediction_stage(double dt){
    Eigen::MatrixXd F(_N_STATES,_N_STATES);

    // jacobian's computation
    F = jacobian_state(_X, dt);

    // Priori state and covariance estimated
    _X = f_prediction_model(_X, dt);

    // Priori covariance
    _P = F*_P*F.transpose() + _E_pred;
}

//-----------------
// correction stage
//-----------------
void AdaptiveOdomFilter::correction_wheel_stage(double dt){
    Eigen::VectorXd Y(_N_WHEEL), hx(_N_WHEEL);
    Eigen::MatrixXd H(_N_WHEEL,_N_STATES), K(_N_STATES,_N_WHEEL), E(_N_WHEEL,_N_WHEEL), S(_N_WHEEL,_N_WHEEL);
    Eigen::MatrixXd I = Eigen::MatrixXd::Identity(_N_STATES,_N_STATES);

    // measure model of wheel odometry (only foward linear velocity)
    hx(0) = _X(6);
    hx(1) = _X(11);
    // measurement
    Y = _wheelMeasure;

    // Jacobian of hx with respect to the states
    H = Eigen::MatrixXd::Zero(_N_WHEEL,_N_STATES);
    H(0,6) = 1; 
    H(1,11) = 1;

    // covariance matrices
    E << _E_wheel;

    // Kalman's gain
    S = H*_P*H.transpose() + E;
    // K = _P*H.transpose()*S.inverse();
    double eps = 1e-12; // ajuste conforme necessário
    Eigen::MatrixXd S_reg = S + eps * Eigen::MatrixXd::Identity(S.rows(), S.cols());
    K = _P * H.transpose() * S_reg.completeOrthogonalDecomposition().pseudoInverse();

    // correction
    _X = _X + K*(Y - hx);
    // _P = _P - K*H*_P;
    _P = (I - K*H)*_P*(I - K*H).transpose(); // forma de Joseph - Evita perda de simetria / negativo-definiteness
}

void AdaptiveOdomFilter::correction_imu_stage(double dt){
    Eigen::Matrix3d S, E;
    Eigen::Vector3d Y, hx;
    Eigen::MatrixXd H(3,_N_STATES), K(_N_STATES,3);
    Eigen::MatrixXd I = Eigen::MatrixXd::Identity(_N_STATES,_N_STATES);

    // measure model
    hx = _X.block(3,0,3,1);

    // IMU measurement
    Y = _imuMeasure.block(6,0,3,1); // roll pitch yaw

    // Jacobian of hx with respect to the states
    H = Eigen::MatrixXd::Zero(3,_N_STATES);
    H.block(0,3,3,3) = Eigen::MatrixXd::Identity(3,3);

    // covariance matrices
    E = _E_imu.block(6,6,3,3);

    // Kalman's gain
    S = H*_P*H.transpose() + E;
    // K = _P*H.transpose()*S.inverse();
    double eps = 1e-12; // ajuste conforme necessário
    Eigen::MatrixXd S_reg = S + eps * Eigen::MatrixXd::Identity(S.rows(), S.cols());
    K = _P * H.transpose() * S_reg.completeOrthogonalDecomposition().pseudoInverse();

    // correction - state
    Eigen::VectorXd residues(3), KR(_N_STATES);
    residues(0) = atan2(sin(Y(0) - hx(0)), cos(Y(0) - hx(0)));
    residues(1) = atan2(sin(Y(1) - hx(1)), cos(Y(1) - hx(1)));
    residues(2) = atan2(sin(Y(2) - hx(2)), cos(Y(2) - hx(2)));
    KR = K*residues;

    _X.block(0,0,3,1) = _X.block(0,0,3,1) + KR.block(0,0,3,1);
    _X(3) = atan2(sin(_X(3) + KR(3)), cos(_X(3) + KR(3)));
    _X(4) = atan2(sin(_X(4) + KR(4)), cos(_X(4) + KR(4)));
    _X(5) = atan2(sin(_X(5) + KR(5)), cos(_X(5) + KR(5)));
    _X.block(6,0,6,1) = _X.block(6,0,6,1) + KR.block(6,0,6,1);

    // X = X + K*(Y - hx); 
    // correction - covariance
    // _P = _P - K*H*_P;
    _P = (I - K*H)*_P*(I - K*H).transpose() + K * E * K.transpose(); // forma de Joseph
}

void AdaptiveOdomFilter::correction_lidar_stage(double dt){
    Eigen::MatrixXd K(_N_STATES,_N_LIDAR), S(_N_LIDAR,_N_LIDAR), G(_N_LIDAR,_N_LIDAR), Gl(_N_LIDAR,_N_LIDAR), Q(_N_LIDAR,_N_LIDAR);
    Eigen::VectorXd Y(_N_LIDAR), hx(_N_LIDAR);
    Eigen::MatrixXd H(_N_LIDAR,_N_STATES); 
    Eigen::MatrixXd I = Eigen::MatrixXd::Identity(_N_STATES,_N_STATES);

    // measure model
    hx = _X.block(6,0,6,1);
    // lidar measurement
    if (_firstLidar){
        _lidarMeasureL = _lidarMeasure;
        _E_lidarL =_E_lidar;
        _firstLidar = false;
    }
    Y = indirect_odometry_measurement(_lidarMeasure, _lidarMeasureL, dt, 'l');

    // Jacobian of hx with respect to the states
    H = Eigen::MatrixXd::Zero(_N_LIDAR,_N_STATES);
    H.block(0,6,6,6) = Eigen::MatrixXd::Identity(_N_LIDAR,_N_LIDAR);

    // Error propagation
    G = jacobian_odometry_measurement(_lidarMeasure, _lidarMeasureL, dt, 'l');
    Gl = jacobian_odometry_measurementL(_lidarMeasure, _lidarMeasureL, dt, 'l');

    Q =  G*_E_lidar*G.transpose() + Gl*_E_lidarL*Gl.transpose();

    // Kalman's gain
    S = H*_P*H.transpose() + Q;
    // K = _P*H.transpose()*S.inverse();
    double eps = 1e-12; // ajuste conforme necessário
    Eigen::MatrixXd S_reg = S + eps * Eigen::MatrixXd::Identity(S.rows(), S.cols());
    K = _P * H.transpose() * S_reg.completeOrthogonalDecomposition().pseudoInverse();

    // correction
    _X = _X + K*(Y - hx);
    // _P = _P - K*H*_P;
    _P = (I - K*H)*_P*(I - K*H).transpose() + K * Q * K.transpose(); // forma de Joseph

    // last measurement
    _lidarMeasureL = _lidarMeasure;
    _E_lidarL = _E_lidar;
}

void AdaptiveOdomFilter::correction_visual_stage(double dt){
    Eigen::MatrixXd K(_N_STATES,_N_VISUAL), S(_N_VISUAL,_N_VISUAL), G(_N_VISUAL,_N_VISUAL), Gl(_N_VISUAL,_N_VISUAL), Q(_N_VISUAL,_N_VISUAL);
    Eigen::VectorXd Y(_N_VISUAL), hx(_N_VISUAL);
    Eigen::MatrixXd H(_N_VISUAL,_N_STATES);
    Eigen::MatrixXd I = Eigen::MatrixXd::Identity(_N_STATES,_N_STATES);

    // measure model
    hx = _X.block(6,0,6,1);
    // visual measurement
    if (_firstVisual){
        _visualMeasureL = _visualMeasure;
        _firstVisual = false;
    }
    Y = indirect_odometry_measurement(_visualMeasure, _visualMeasureL, dt, 'v');

    // Jacobian of hx with respect to the states
    H = Eigen::MatrixXd::Zero(_N_VISUAL,_N_STATES);
    H.block(0,6,6,6) = Eigen::MatrixXd::Identity(_N_VISUAL,_N_VISUAL);

    // Error propagation
    G = jacobian_odometry_measurement(_visualMeasure, _visualMeasureL, dt, 'v');
    Gl = jacobian_odometry_measurementL(_visualMeasure, _visualMeasureL, dt, 'v');

    Q =  G*_E_visual*G.transpose() + Gl*_E_visualL*Gl.transpose();

    // Kalman's gain
    S = H*_P*H.transpose() + Q;
    // K = _P*H.transpose()*S.inverse();
    double eps = 1e-12; // ajuste conforme necessário
    Eigen::MatrixXd S_reg = S + eps * Eigen::MatrixXd::Identity(S.rows(), S.cols());
    K = _P * H.transpose() * S_reg.completeOrthogonalDecomposition().pseudoInverse();

    // correction
    _X = _X + K*(Y - hx);
    // _P = _P - K*H*_P;
    _P = (I - K*H)*_P*(I - K*H).transpose(); // forma de Joseph

    // last measurement
    _visualMeasureL = _visualMeasure;
    _E_visualL = _E_visual;
}

//---------
// Models
//---------
VectorXd AdaptiveOdomFilter::f_prediction_model(VectorXd x, double dt){ 
    // state: {x, y, z, roll, pitch, yaw, vx, vy, vz, wx, wy, wz}
    //        {         (world)         }{        (body)        }
    Eigen::Matrix3d R, Rx, Ry, Rz, J;
    Eigen::VectorXd xp(_N_STATES), Axdt(_N_STATES), xNew(_N_STATES);
    Eigen::MatrixXd A(6,6);

    xNew = x; // robo diferencial - monociclo; para outros modelos alterar aqui
    xNew.block(7,0,3,1) = Eigen::Vector3d::Zero(); // vy, vz, wx, wy igual a zero.

    // Rotation matrix
    Rx = Eigen::AngleAxisd(x(3), Eigen::Vector3d::UnitX());
    Ry = Eigen::AngleAxisd(x(4), Eigen::Vector3d::UnitY());
    Rz = Eigen::AngleAxisd(x(5), Eigen::Vector3d::UnitZ());
    R = Rz*Ry*Rx;
    
    // Jacobian matrix
    J << 1.0, sin(x(3))*tan(x(4)), cos(x(3))*tan(x(4)),
            0.0, cos(x(3)), -sin(x(3)),
            0.0, sin(x(3))/cos(x(4)), cos(x(3))/cos(x(4));
    
    // model
    A = Eigen::MatrixXd::Identity(6,6);
    A.block(0,0,3,3) = R;
    A.block(3,3,3,3) = J;

    // displacement
    Axdt = A*xNew.block(6,0,6,1)*dt;
    // position
    xp.block(0,0,3,1) = x.block(0,0,3,1) + Axdt.block(0,0,3,1);
    // orientation
    xp(3) = atan2(sin(x(3) + Axdt(3)), cos(x(3) + Axdt(3)));
    xp(4) = atan2(sin(x(4) + Axdt(4)), cos(x(4) + Axdt(4)));
    xp(5) = atan2(sin(x(5) + Axdt(5)), cos(x(5) + Axdt(5))); 
    // velocity
    xp.block(6,0,6,1) = x.block(6,0,6,1);

    return xp;
}

VectorXd AdaptiveOdomFilter::indirect_odometry_measurement(VectorXd u, VectorXd ul, double dt, char type){
    Eigen::Matrix3d R, Rx, Ry, Rz, J;
    Eigen::VectorXd up, u_diff; 
    Eigen::MatrixXd A; 

    // model
    switch (type){
        case 'l':
            up.resize(_N_LIDAR);
            u_diff.resize(_N_LIDAR);
            A.resize(_N_LIDAR,_N_LIDAR); 
            A = Eigen::MatrixXd::Zero(_N_LIDAR,_N_LIDAR);

            break;
        case 'v':
            up.resize(_N_VISUAL);
            u_diff.resize(_N_VISUAL);
            A.resize(_N_VISUAL,_N_VISUAL); 
            A = Eigen::MatrixXd::Zero(_N_VISUAL,_N_VISUAL);
            
            break;
        
        default:
            break;
    }

    // Rotation matrix
    Rx = Eigen::AngleAxisd(ul(3), Eigen::Vector3d::UnitX());
    Ry = Eigen::AngleAxisd(ul(4), Eigen::Vector3d::UnitY());
    Rz = Eigen::AngleAxisd(ul(5), Eigen::Vector3d::UnitZ());
    R = Rz*Ry*Rx;
    
    // Jacobian matrix
    J << 1.0, sin(ul(3))*tan(ul(4)), cos(ul(3))*tan(ul(4)),
            0.0, cos(ul(3)), -sin(ul(3)),
            0.0, sin(ul(3))/cos(ul(4)), cos(ul(3))/cos(ul(4));
    
    u_diff.block(0,0,3,1) = (u.block(0,0,3,1) - ul.block(0,0,3,1));
    u_diff(3) = atan2(sin(u(3) - ul(3)),cos(u(3) - ul(3)));
    u_diff(4) = atan2(sin(u(4) - ul(4)),cos(u(4) - ul(4)));
    u_diff(5) = atan2(sin(u(5) - ul(5)),cos(u(5) - ul(5)));

    // model
    switch (type){
        case 'l':                
            u_diff = alpha_lidar*u_diff;

            break;
        case 'v':
            u_diff = alpha_visual*u_diff;

            break;
        
        default:
            break;
    }

    A.block(0,0,3,3) = R.transpose();
    A.block(3,3,3,3) = J.inverse();

    up = A*u_diff/dt;

    return up;

}

//----------
// Jacobians
//----------
MatrixXd AdaptiveOdomFilter::jacobian_state(VectorXd x, double dt){
    Eigen::MatrixXd J(_N_STATES,_N_STATES);
    Eigen::VectorXd f0(_N_STATES), f1(_N_STATES), x_plus(_N_STATES);

    f0 = f_prediction_model(x, dt);

    double delta = 0.0001;
    for (size_t i = 0; i < _N_STATES; i++){
        x_plus = x;
        x_plus(i) = x_plus(i) + delta;

        f1 = f_prediction_model(x_plus, dt);
        
        J.block(0,i,_N_STATES,1) = (f1 - f0)/delta;       
        J(3,i) = atan2(sin(f1(3) - f0(3)),cos(f1(3) - f0(3)))/delta;
        J(4,i) = atan2(sin(f1(4) - f0(4)),cos(f1(4) - f0(4)))/delta;
        J(5,i) = atan2(sin(f1(5) - f0(5)),cos(f1(5) - f0(5)))/delta; 
    }

    return J;
}

MatrixXd AdaptiveOdomFilter::jacobian_odometry_measurement(VectorXd u, VectorXd ul, double dt, char type){
    Eigen::MatrixXd J;
    Eigen::VectorXd f0(_N_LIDAR), f1(_N_LIDAR), u_plus(_N_LIDAR);
    double delta;

    switch (type){
        case 'l':
            J.resize(_N_LIDAR,_N_LIDAR);
            f0.resize(_N_LIDAR);
            f1.resize(_N_LIDAR);
            u_plus.resize(_N_LIDAR);

            f0 = indirect_odometry_measurement(u, ul, dt, 'l');

            delta = 0.0000001;
            for (size_t i = 0; i < _N_LIDAR; i++){
                u_plus = u;
                u_plus(i) = u_plus(i) + delta;

                f1 = indirect_odometry_measurement(u_plus, ul, dt, 'l');
            
                J.block(0,i,_N_LIDAR,1) = (f1 - f0)/delta;       
                J(3,i) = atan2(sin(f1(3) - f0(3)), cos(f1(3) - f0(3)))/delta;
                J(4,i) = atan2(sin(f1(4) - f0(4)), cos(f1(4) - f0(4)))/delta;
                J(5,i) = atan2(sin(f1(5) - f0(5)), cos(f1(5) - f0(5)))/delta; 
            }

            break;
        case 'v':
            J.resize(_N_VISUAL,_N_VISUAL);
            f0.resize(_N_VISUAL);
            f1.resize(_N_VISUAL);
            u_plus.resize(_N_VISUAL);

            f0 = indirect_odometry_measurement(u, ul, dt, 'v');

            delta = 0.0000001;
            for (size_t i = 0; i < _N_VISUAL; i++){
                u_plus = u;
                u_plus(i) = u_plus(i) + delta;

                f1 = indirect_odometry_measurement(u_plus, ul, dt, 'v');
            
                J.block(0,i,_N_VISUAL,1) = (f1 - f0)/delta;       
                J(3,i) = atan2(sin(f1(3) - f0(3)),cos(f1(3) - f0(3)))/delta;
                J(4,i) = atan2(sin(f1(4) - f0(4)),cos(f1(4) - f0(4)))/delta;
                J(5,i) = atan2(sin(f1(5) - f0(5)),cos(f1(5) - f0(5)))/delta; 
            }

            break;
        
        default:
            break;
    }

    return J;
}

MatrixXd AdaptiveOdomFilter::jacobian_odometry_measurementL(VectorXd u, VectorXd ul, double dt, char type){ 
    Eigen::MatrixXd J;
    Eigen::VectorXd f0(_N_LIDAR), f1(_N_LIDAR), ul_plus(_N_LIDAR);
    double delta;

    switch (type){
        case 'l':
            J.resize(_N_LIDAR,_N_LIDAR);
            f0.resize(_N_LIDAR);
            f1.resize(_N_LIDAR);
            ul_plus.resize(_N_LIDAR);

            f0 = indirect_odometry_measurement(u, ul, dt, 'l');

            delta = 0.0000001;
            for (size_t i = 0; i < _N_LIDAR; i++){
                ul_plus = ul;
                ul_plus(i) = ul_plus(i) + delta;

                f1 = indirect_odometry_measurement(u, ul_plus, dt, 'l');
            
                J.block(0,i,_N_LIDAR,1) = (f1 - f0)/delta;       
                J(3,i) = atan2(sin(f1(3) - f0(3)), cos(f1(3) - f0(3)))/delta;
                J(4,i) = atan2(sin(f1(4) - f0(4)), cos(f1(4) - f0(4)))/delta;
                J(5,i) = atan2(sin(f1(5) - f0(5)), cos(f1(5) - f0(5)))/delta;
            }

            break;
        case 'v':
            J.resize(_N_VISUAL,_N_VISUAL);
            f0.resize(_N_VISUAL);
            f1.resize(_N_VISUAL);
            ul_plus.resize(_N_VISUAL);

            f0 = indirect_odometry_measurement(u, ul, dt, 'v');

            delta = 0.0000001;
            for (size_t i = 0; i < _N_VISUAL; i++){
                ul_plus = ul;
                ul_plus(i) = ul_plus(i) + delta;

                f1 = indirect_odometry_measurement(u, ul_plus, dt, 'v');
            
                J.block(0,i,_N_VISUAL,1) = (f1 - f0)/delta;       
                J(3,i) = atan2(sin(f1(3) - f0(3)), cos(f1(3) - f0(3)))/delta;
                J(4,i) = atan2(sin(f1(4) - f0(4)), cos(f1(4) - f0(4)))/delta;
                J(5,i) = atan2(sin(f1(5) - f0(5)), cos(f1(5) - f0(5)))/delta;
            }

            break;
        
        default:
            break;
    }

    return J;
}

//--------------
// run
//--------------
void AdaptiveOdomFilter::run(){
    // rate (ROS 2)
    rclcpp::Rate r(freq);

    // use a steady (monotonic) clock to compute dt
    rclcpp::Clock clock(RCL_STEADY_TIME);
    double t_last = clock.now().seconds();
    double t_now;
    double dt_now;

    double imu_count, wheel_count, lidar_count, visual_count;
    bool imu_fail_msg, wheel_fail_msg, lidar_fail_msg, visual_fail_msg;
    imu_count = 0;
    wheel_count = 0;
    lidar_count = 0;
    visual_count = 0;
    imu_fail_msg = false;
    wheel_fail_msg = false;
    lidar_fail_msg = false;
    visual_fail_msg = false;

    while (_running && rclcpp::ok())
    {
        // prediction stage
        t_now = clock.now().seconds();
        dt_now = t_now - t_last;
        t_last = t_now;

        if(imu_count >= _imu_dt*1.2) {
            imu_fail_msg = true;
        }

        if(wheel_count >= _wheel_dt*1.2) {
            wheel_fail_msg = true;
        }

        if(lidar_count >= _lidar_dt*1.2) {
            lidar_fail_msg = true;
        }

        if(visual_count >= _visual_dt*1.2) {
            visual_fail_msg = true;
        }

        if ((_imuActivated || _wheelActivated || _lidarActivated || _visualActivated) && (!(imu_fail_msg && wheel_fail_msg && lidar_fail_msg && visual_fail_msg))){
            prediction_stage(dt_now);
        }
        else {
            // printf("Sensors failed, waiting for new data...\n");
            continue;
        }

        {
            std::lock_guard<std::mutex> lock(_mutex);
            //Correction IMU
            if (enableImu && _imuActivated && _imuNew){
                correction_imu_stage(_imu_dt);
                _imuNew =  false;
                imu_fail_msg = false;
                imu_count = 0;
            }

            // Correction wheel
            if (enableWheel && _wheelActivated && _wheelNew){                
                correction_wheel_stage(_wheel_dt);
                _wheelNew =  false;
                wheel_fail_msg = false;
                wheel_count = 0;
            }

            //Corection Visual
            if (enableVisual && _visualActivated && _visualNew){                
                correction_visual_stage(_visual_dt);
                _visualNew =  false;
                visual_fail_msg = false;
                visual_count = 0;
            }

            //Corection LiDAR
            if (enableLidar && _lidarActivated && _lidarNew){                
                correction_lidar_stage(_lidar_dt);
                _lidarNew =  false;
                lidar_fail_msg = false;
                lidar_count = 0;
            }
        }
        
        // counters increment
        imu_count += dt_now;
        wheel_count += dt_now;
        lidar_count += dt_now;
        visual_count += dt_now;

        // out data
        _V = _X;
        _PV = _P;

        // final marker 
        r.sleep();        
    }
}

//---------------------------
// covariances functions
//---------------------------
MatrixXd AdaptiveOdomFilter::adaptive_covariance(double fCorner, double fSurf){
    Eigen::MatrixXd Q(6,6);
    double cov_x, cov_y, cov_z, cov_phi, cov_psi, cov_theta;
    
    // heuristic
    switch(lidar_type_func){
        case 0:
            cov_x     = lidarG*((nCorner - min(fCorner,nCorner))/nCorner + l_min);
            cov_y     = lidarG*((nCorner - min(fCorner,nCorner))/nCorner + l_min);
            cov_psi   = lidarG*((nCorner - min(fCorner,nCorner))/nCorner + l_min);
            cov_z     = lidarG*((nSurf - min(fSurf,nSurf))/nSurf + l_min);
            cov_phi   = lidarG*((nSurf - min(fSurf,nSurf))/nSurf + l_min);
            cov_theta = lidarG*((nSurf - min(fSurf,nSurf))/nSurf + l_min);
            break;
        case 1:
            cov_x     = lidarG*exp(-lidarG*(nCorner - min(fCorner,nCorner))/nCorner) + l_min;
            cov_y     = lidarG*exp(-lidarG*(nCorner - min(fCorner,nCorner))/nCorner) + l_min;
            cov_psi   = lidarG*exp(-lidarG*(nCorner - min(fCorner,nCorner))/nCorner) + l_min;
            cov_z     = lidarG*exp(-lidarG*(nSurf -   min(fSurf,nSurf))/nSurf) + l_min;
            cov_phi   = lidarG*exp(-lidarG*(nSurf -   min(fSurf,nSurf))/nSurf) + l_min;
            cov_theta = lidarG*exp(-lidarG*(nSurf -   min(fSurf,nSurf))/nSurf) + l_min;
            break;
    }
    
    Q = MatrixXd::Zero(6,6);
    Q(0,0) = Gx*cov_x;
    Q(1,1) = Gy*cov_y;
    Q(2,2) = Gz*cov_z;
    Q(3,3) = Gphi*cov_phi;
    Q(4,4) = Gtheta*cov_theta;
    Q(5,5) = Gpsi*cov_psi;

    return Q;
}

MatrixXd AdaptiveOdomFilter::adaptive_visual_covariance(double IntensityIn){
    Eigen::MatrixXd Q(6,6);
    double cov, Intensity;

    Intensity = (IntensityIn - minIntensity)/(maxIntensity - minIntensity);
    
    // heuristic
    switch(visual_type_func){
        case 0:
            cov = visualG*((1.0 - min(Intensity,1.0))/1.0 + l_min);
            break;
        case 1:
            cov = visualG*exp(-visualG*Intensity) + l_min;
            break;
    }
    
    Q = MatrixXd::Zero(6,6);
    Q(0,0) = Gvx*cov;
    Q(1,1) = Gvy*cov;
    Q(2,2) = Gvz*cov;
    Q(3,3) = Gvphi*cov;
    Q(4,4) = Gvtheta*cov;
    Q(5,5) = Gvpsi*cov;

    return Q;
}

MatrixXd AdaptiveOdomFilter::wheelOdometryAdaptiveCovariance(double omegaz_wheel_odom, double omegaz_imu){
    Eigen::MatrixXd E(2,2);

    E(0,0) = gamma_vx * abs(omegaz_wheel_odom - omegaz_imu) + delta_vx;
    E(1,1) = gamma_omegaz * abs(omegaz_wheel_odom - omegaz_imu) + delta_omegaz;

    return E;
}     

//**************************
// PUBLIC FUNCTIONS
//**************************
//----------
// Datas
//----------
void AdaptiveOdomFilter::correction_imu_data(VectorXd imu, MatrixXd E_imu, double dt){
    std::lock_guard<std::mutex> lock(_mutex);
    // activation
    if (!_imuActivated){
        _imuActivated = true;
    }

    // update data
    _imuMeasure = imu;
    _E_imu = E_imu;
    _imu_dt = dt;

    //New measure
    _imuNew = true;
}

void AdaptiveOdomFilter::correction_wheel_data(VectorXd wheel_odom, MatrixXd E_wheel, double dt, double omegaz_imu){
    // mutex
    std::lock_guard<std::mutex> lock(_mutex);

    // activation
    if (!_wheelActivated){
        _wheelActivated = true;
    }

    // update data
    _wheelMeasure = wheel_odom;

    if (wheel_type_func==1){
        _E_wheel = E_wheel;
    }else{
        double omegaz_wheel_odom = wheel_odom(1);
        _E_wheel = wheelOdometryAdaptiveCovariance(omegaz_wheel_odom, omegaz_imu);
    }

    _wheel_dt = dt;

    //New measure
    _wheelNew = true;
}

void AdaptiveOdomFilter::correction_lidar_data(VectorXd lidar_odom, MatrixXd E_lidar, double dt, double corner, double surf){
    std::lock_guard<std::mutex> lock(_mutex);
    // activation
    if (!_lidarActivated){
        _lidarActivated = true;
    }

    // update data
    _lidarMeasure = lidar_odom;
    if (lidar_type_func==2){
        _E_lidar = lidarG*E_lidar;
    }else{
        Eigen::MatrixXd E_lidar(6,6);
        _E_lidar = adaptive_covariance(corner, surf);                
    }

    _lidar_dt = dt;

    //New measure
    _lidarNew = true;
}

void AdaptiveOdomFilter::correction_visual_data(VectorXd visual_odom, MatrixXd E_visual, double dt, double averageIntensity){
    // mutex
    std::lock_guard<std::mutex> lock(_mutex);

    // activation
    if (!_visualActivated){
        _visualActivated = true;
    }

    // update data
    _visualMeasure = visual_odom;

    if (visual_type_func==2){
        _E_visual = E_visual;
    }else{
        Eigen::MatrixXd E_visual(6,6);
        _E_visual = adaptive_visual_covariance(averageIntensity);
    }

    _visual_dt = dt;

    //New measure
    _visualNew = true;
}

//------------------
// filter control - verfica aqui
// -----------------
void AdaptiveOdomFilter::get_state(VectorXd &X_state, MatrixXd &E_state) {
    std::lock_guard<std::mutex> lock(_mutex);
    // get the last state updated
    X_state = _X;
    E_state = _P;
}

void AdaptiveOdomFilter::set_initial_state(VectorXd X_state, MatrixXd E_state){
    std::lock_guard<std::mutex> lock(_mutex);
    // priori stare
    _X = X_state;
    _P = E_state;
}

void AdaptiveOdomFilter::start() {
    _running = true;
    _thread = std::thread(&AdaptiveOdomFilter::run, this);
}

void AdaptiveOdomFilter::stop() {
    _running = false;
    if (_thread.joinable()) {
        _thread.join();
    }
}
