/* Stateless position and Fit++ collision geometry. */
var kgLayoutGeometry = (function() {
  "use strict";
  function validLayoutPosition(position) {
    return Boolean(
      position &&
      Number.isFinite(Number(position.x)) &&
      Number.isFinite(Number(position.y))
    );
  }

  function copyLayoutPosition(position) {
    return {x: Number(position.x), y: Number(position.y)};
  }

  function reducedContractionExtents(extents) {
    var left = Number(extents.left) * 0.9;
    var right = Number(extents.right) * 0.9;
    var top = Number(extents.top);
    var bottom = Number(extents.bottom) * 0.9;
    return {
      left: left,
      right: right,
      top: top,
      bottom: bottom,
      width: left + right,
      height: top + bottom
    };
  }

  function contractionClearance(left, right) {
    var characteristicSize = Math.max(
      Math.min(left.width, left.height),
      Math.min(right.width, right.height)
    );
    return Math.max(60, Math.min(240, characteristicSize * 0.18));
  }

  function segmentEntryParameter(start, end, bounds) {
    var delta = {x: end.x - start.x, y: end.y - start.y};
    var entry = 0;
    var exit = 1;
    [
      {origin: start.x, delta: delta.x, min: bounds.left, max: bounds.right},
      {origin: start.y, delta: delta.y, min: bounds.top, max: bounds.bottom}
    ].forEach(function(axis) {
      if (entry > exit) { return; }
      if (Math.abs(axis.delta) < 0.000001) {
        if (axis.origin < axis.min || axis.origin > axis.max) {
          entry = 2;
          exit = 1;
        }
        return;
      }
      var first = (axis.min - axis.origin) / axis.delta;
      var second = (axis.max - axis.origin) / axis.delta;
      if (first > second) {
        var swap = first;
        first = second;
        second = swap;
      }
      entry = Math.max(entry, first);
      exit = Math.min(exit, second);
    });
    if (entry > exit || exit < 0 || entry > 1) { return null; }
    return Math.max(0, entry);
  }

  function contractionObstacleBounds(movingExtents, obstacle) {
    var clearance = contractionClearance(movingExtents, obstacle.extents);
    return {
      left: obstacle.position.x - obstacle.extents.left - clearance - movingExtents.right,
      right: obstacle.position.x + obstacle.extents.right + clearance + movingExtents.left,
      top: obstacle.position.y - obstacle.extents.top - clearance - movingExtents.bottom,
      bottom: obstacle.position.y + obstacle.extents.bottom + clearance + movingExtents.top
    };
  }

  function contractionCollisionEntry(start, end, movingExtents, obstacle) {
    return segmentEntryParameter(
      start,
      end,
      contractionObstacleBounds(movingExtents, obstacle)
    );
  }

  function contractionPositionInsideBounds(position, bounds) {
    return position.x > bounds.left && position.x < bounds.right &&
      position.y > bounds.top && position.y < bounds.bottom;
  }

  function clearInitialContractionCollision(start, anchor, extents, placed) {
    var radial = {x: start.x - anchor.x, y: start.y - anchor.y};
    var length = Math.hypot(radial.x, radial.y);
    if (length < 0.000001) { return copyLayoutPosition(start); }
    var direction = {x: radial.x / length, y: radial.y / length};
    var position = copyLayoutPosition(start);

    for (var iteration = 0; iteration < 24; iteration += 1) {
      var overlapping = placed.map(function(obstacle) {
        return contractionObstacleBounds(extents, obstacle);
      }).filter(function(bounds) {
        return contractionPositionInsideBounds(position, bounds);
      });
      if (overlapping.length === 0) { break; }

      var travel = 0;
      overlapping.forEach(function(bounds) {
        var horizontalExit = Infinity;
        var verticalExit = Infinity;
        if (direction.x > 0.000001) {
          horizontalExit = (bounds.right - position.x) / direction.x;
        } else if (direction.x < -0.000001) {
          horizontalExit = (bounds.left - position.x) / direction.x;
        }
        if (direction.y > 0.000001) {
          verticalExit = (bounds.bottom - position.y) / direction.y;
        } else if (direction.y < -0.000001) {
          verticalExit = (bounds.top - position.y) / direction.y;
        }
        travel = Math.max(travel, Math.min(horizontalExit, verticalExit));
      });
      if (!Number.isFinite(travel) || travel < 0) { break; }
      position = {
        x: position.x + direction.x * (travel + 0.5),
        y: position.y + direction.y * (travel + 0.5)
      };
    }
    return position;
  }

  return {
    validLayoutPosition: validLayoutPosition,
    copyLayoutPosition: copyLayoutPosition,
    reducedContractionExtents: reducedContractionExtents,
    contractionClearance: contractionClearance,
    segmentEntryParameter: segmentEntryParameter,
    contractionObstacleBounds: contractionObstacleBounds,
    contractionCollisionEntry: contractionCollisionEntry,
    contractionPositionInsideBounds: contractionPositionInsideBounds,
    clearInitialContractionCollision: clearInitialContractionCollision
  };
})();
