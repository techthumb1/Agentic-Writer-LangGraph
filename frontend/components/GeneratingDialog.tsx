import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Loader2 } from "lucide-react";

interface Props {
  open: boolean;
}

export default function GeneratingDialog({ open }: Props) {
  return (
    <Dialog open={open}>
      <DialogContent aria-describedby="generation-description">
        <DialogHeader>
          <DialogTitle>Generating Content...</DialogTitle>
          <DialogDescription id="generation-description">
            Please wait while we craft your content.
          </DialogDescription>
        </DialogHeader>

        <div className="flex justify-center items-center py-8">
          <Loader2 className="h-10 w-10 animate-spin text-blue-500" />
        </div>
      </DialogContent>
    </Dialog>
  );
}
