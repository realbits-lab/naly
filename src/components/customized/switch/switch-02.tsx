import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import React from "react";

const SwitchWithLabelDemo = () => {
  return (
    <div className="flex items-center gap-3">
      <Switch id="enable-feature" />
      <Label htmlFor="enable-feature">Enable Feature</Label>
    </div>
  );
};

export default SwitchWithLabelDemo;
