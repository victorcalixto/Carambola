#pragma once

namespace carambola {

class Section {
public:
    Section(double area, double iy, double iz, double torsional_constant);

    virtual ~Section() = default;

    double area() const;
    double iy() const;
    double iz() const;
    double torsional_constant() const;

private:
    double area_;
    double iy_;
    double iz_;
    double torsional_constant_;
};

class RectangularSection : public Section {
public:
    RectangularSection(double width, double height);

    double width() const;
    double height() const;

private:
    double width_;
    double height_;
};

class CircularSection : public Section {
public:
    explicit CircularSection(double radius);

    double radius() const;

private:
    double radius_;
};

}
