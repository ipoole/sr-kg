/* Pure graph-space geometry: no visibility, camera or persistent-state writes. */
var kgModuleGeometry = (function() {
  function finitePoint(point) {
    return point && Number.isFinite(point.x) && Number.isFinite(point.y);
  }

  function footprint(members, anchor, padding) {
    anchor = finitePoint(anchor) ? anchor : {x: 0, y: 0};
    padding = Number.isFinite(padding) ? Math.max(0, padding) : 1;
    var left = Infinity, right = -Infinity, top = Infinity, bottom = -Infinity;
    var defaults = {left: 125, right: 125, top: 100, bottom: 200};
    (members || []).forEach(function(member) {
      if (!member || !finitePoint(member.position)) { return; }
      var extents = {};
      Object.keys(defaults).forEach(function(side) {
        var value = member.extents && member.extents[side];
        extents[side] = Number.isFinite(value) && value >= 0 ? value : defaults[side];
      });
      left = Math.min(left, member.position.x - extents.left - padding);
      right = Math.max(right, member.position.x + extents.right + padding);
      top = Math.min(top, member.position.y - extents.top - padding);
      bottom = Math.max(bottom, member.position.y + extents.bottom + padding);
    });
    if (!Number.isFinite(left)) {
      left = anchor.x - 150; right = anchor.x + 150;
      top = anchor.y - 90; bottom = anchor.y + 90;
    }
    var x = (left + right) / 2, y = (top + bottom) / 2;
    return {
      left: left, right: right, top: top, bottom: bottom,
      width: Math.max(1, right - left), height: Math.max(1, bottom - top),
      x: x, y: y, offset: {x: x - anchor.x, y: y - anchor.y}
    };
  }
  return {footprint: footprint};
})();
