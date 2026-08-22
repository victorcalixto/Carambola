#include <carambola/section.hpp>

#include <cmath>
#include <stdexcept>

namespace carambola {

Section::Section(
    double area,
    double iy,
    double iz,
    double torsional_constant
)
    : area_(area),
      iy_(iy),
      iz_(iz),
      torsional_constant_(torsional_constant)
{
    if (area_ <= 0.0) {
        throw std::invalid_argument("Section area must be positive.");
    }

    if (iy_ <= 0.0 || iz_ <= 0.0) {
        throw std::invalid_argument(
            "Section second moments of area must be positive."
        );
    }

    if (torsional_constant_ <= 0.0) {
        throw std::invalid_argument(
            "Section torsional constant must be positive."
        );
    }
}

double Section::area() const
{
    return area_;
}

double Section::iy() const
{
    return iy_;
}

double Section::iz() const
{
    return iz_;
}

double Section::torsional_constant() const
{
    return torsional_constant_;
}

RectangularSection::RectangularSection(double width, double height)
    : Section(
          width * height,
          width * std::pow(height, 3) / 12.0,
          height * std::pow(width, 3) / 12.0,
          width * std::pow(height, 3) / 3.0
      ),
      width_(width),
      height_(height)
{
    if (width_ <= 0.0 || height_ <= 0.0) {
        throw std::invalid_argument(
            "Rectangle width and height must be positive."
        );
    }
}

double RectangularSection::width() const
{
    return width_;
}

double RectangularSection::height() const
{
    return height_;
}

CircularSection::CircularSection(double radius)
    : Section(
          M_PI * radius * radius,
          M_PI * std::pow(radius, 4) / 4.0,
          M_PI * std::pow(radius, 4) / 4.0,
          M_PI * std::pow(radius, 4) / 2.0
      ),
      radius_(radius)
{
    if (radius_ <= 0.0) {
        throw std::invalid_argument(
            "Circle radius must be positive."
        );
    }
}

double CircularSection::radius() const
{
    return radius_;
}

}
