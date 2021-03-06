#include "Python.h"
#include "StrideSearchUtilities.h"
#include <cmath>

// static const double deg2rad = std::atan(1.0) / 45.0;

void llToXYZ(double& x, double& y, double& z, const double& lat, const double& lon){
    x = std::cos(deg2rad * lat) * std::cos(deg2rad * lon);
    y = std::cos(deg2rad * lat) * std::sin(deg2rad * lon);
    z = std::sin(deg2rad * lat);
}

double atan4( const double y, const double x)
{
    double result = 0.0;
    if ( x == 0.0)
    {
        if ( y > 0.0)
            result = 0.5 * PI;
        else if ( y < 0.0 )
            result = 1.5 * PI;
        else if ( y == 0.0 )
            result = 0.0;
    }
    else if ( y == 0 )
    {
        if ( x > 0.0 )
            result = 0.0;
        else if ( x < 0.0 )
            result = PI;
    }
    else
    {
        double theta = std::atan2( std::abs(y), std::abs(x));
        if ( x > 0.0 && y > 0.0 )
            result = theta;
        else if ( x < 0.0 && y > 0.0 )
            result = PI - theta;
        else if ( x < 0.0 && y < 0.0 )
            result = PI + theta;
        else if ( x > 0.0 && y < 0.0 )
            result = 2.0 * PI - theta;
    }
    return result;
}

void XyzToLL(double& lat, double& lon, const double& x, const double& y, const double& z) {
    lat = std::atan2(z, std::sqrt(x*x + y*y));
    lon = atan4(y, x);
};

double sphereDistance(const double latA, const double lonA, const double latB, const double lonB){
    if (std::abs(latB - latA) < ZERO_TOL && std::abs(lonB - lonA) < ZERO_TOL)
        return 0.0;
    else {
        double xA, yA, zA;
        double xB, yB, zB;
        llToXYZ(xA, yA, zA, latA, lonA);
        llToXYZ(xB, yB, zB, latB, lonB);
        
        const double cp1 = yA * zB - yB * zA;
        const double cp2 = xB * zA - xA * zB;
        const double cp3 = xA * yB - xB * yA;
        const double cpnorm = std::sqrt(cp1 * cp1 + cp2 * cp2 + cp3 * cp3);
        
        const double dotProd = xA * xB + yA * yB + zA * zB;
        
        return EARTH_RADIUS_KM * std::atan2(cpnorm, dotProd);
    }
}

static PyObject* wrap_sphereDistance(PyObject* self, PyObject* args) {
    double latA, lonA, latB, lonB;
    double result;
    /* Python -> C++ conversion */
    if (!PyArg_ParseTuple(args, "dddd", &latA, &lonA, &latB, &lonB))
        return NULL;
        
    /* call c++ function */
    result = sphereDistance(latA, lonA, latB, lonB);
    
    /* c++ -> Python conversion */
    return Py_BuildValue("d", result);
}

static PyMethodDef UtilMethods[] = { {"sphereDistance", wrap_sphereDistance, METH_VARARGS, 
    "Calculate the great-circle distance between two lat-lon locations (in degrees)"}, {NULL, NULL, 0, NULL} };

PyMODINIT_FUNC initStrideSearchUtilities(void) {
    (void) Py_InitModule("StrideSearchUtilities", UtilMethods);
}



