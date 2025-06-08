import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { ExclamationTriangleIcon } from "@radix-ui/react-icons";

export default function AlertWarningDemo() {
  return (
    <Alert className="border-amber-500/50 text-amber-500 dark:border-amber-500 [&>svg]:text-amber-500">
      <ExclamationTriangleIcon className="h-4 w-4" />
      <AlertTitle>Proceed with Caution</AlertTitle>
      <AlertDescription>
        This action might have unintended consequences.
      </AlertDescription>
    </Alert>
  );
}
