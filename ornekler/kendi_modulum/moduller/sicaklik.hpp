// sicaklik.hpp - sicaklik modülünün C++ karşılığı (PC ve Arduino)
#pragma once
#include "ekin.hpp"

namespace sicaklik {

const double MUTLAK_SIFIR = -273.15;

inline ekin::ondalik fahrenhayta(ekin::ondalik c) { return c * 9.0 / 5.0 + 32.0; }
inline ekin::ondalik santigrata(ekin::ondalik f) { return (f - 32.0) * 5.0 / 9.0; }
inline ekin::ondalik hissedilen(ekin::ondalik t, ekin::ondalik v) { return t - 0.7 * sqrt(v); }

}  // namespace sicaklik
