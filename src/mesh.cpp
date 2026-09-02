#include <carambola/mesh.hpp>

#include <stdexcept>


namespace carambola {

ShellMesh rectangular_shell_mesh(
    double width,
    double height,
    std::size_t nx,
    std::size_t ny
)
{
    if (width <= 0.0) {
        throw std::invalid_argument(
            "Mesh width must be positive"
        );
    }

    if (height <= 0.0) {
        throw std::invalid_argument(
            "Mesh height must be positive"
        );
    }

    if (nx == 0) {
        throw std::invalid_argument(
            "Mesh nx must be greater than zero"
        );
    }

    if (ny == 0) {
        throw std::invalid_argument(
            "Mesh ny must be greater than zero"
        );
    }

    ShellMesh mesh;

    const std::size_t vertex_count =
        (nx + 1) * (ny + 1);

    const std::size_t face_count =
        2 * nx * ny;

    mesh.vertices.reserve(
        vertex_count
    );

    mesh.faces.reserve(
        face_count
    );

    const double dx =
        width / static_cast<double>(nx);

    const double dy =
        height / static_cast<double>(ny);

    // Row-major vertex ordering:
    //
    // y
    // ^
    //
    // 6 -- 7 -- 8
    // 3 -- 4 -- 5
    // 0 -- 1 -- 2  -> x
    //
    for (
        std::size_t j = 0;
        j <= ny;
        ++j
    ) {
        const double y =
            static_cast<double>(j) * dy;

        for (
            std::size_t i = 0;
            i <= nx;
            ++i
        ) {
            const double x =
                static_cast<double>(i) * dx;

            mesh.vertices.emplace_back(
                x,
                y,
                0.0
            );
        }
    }

    const auto vertex_index =
        [nx](
            std::size_t i,
            std::size_t j
        ) -> std::size_t
    {
        return j * (nx + 1) + i;
    };

    for (
        std::size_t j = 0;
        j < ny;
        ++j
    ) {
        for (
            std::size_t i = 0;
            i < nx;
            ++i
        ) {
            const std::size_t n0 =
                vertex_index(i, j);

            const std::size_t n1 =
                vertex_index(i + 1, j);

            const std::size_t n2 =
                vertex_index(i + 1, j + 1);

            const std::size_t n3 =
                vertex_index(i, j + 1);

            // Both triangles are counter-clockwise
            // when viewed from +Z.
            //
            // n3 ----- n2
            // |      / |
            // |    /   |
            // |  /     |
            // n0 ----- n1

            mesh.faces.emplace_back(
                static_cast<int>(n0),
                static_cast<int>(n1),
                static_cast<int>(n2)
            );

            mesh.faces.emplace_back(
                static_cast<int>(n0),
                static_cast<int>(n2),
                static_cast<int>(n3)
            );
        }
    }

    return mesh;
}

}
