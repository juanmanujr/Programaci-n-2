Public Class frmMenu
    Private Sub ContactoToolStripMenuItem1_Click(sender As Object, e As EventArgs) Handles ContactoToolStripMenuItem1.Click
        frmContacto.Show()
    End Sub

    Private Sub DirecciónToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles DirecciónToolStripMenuItem.Click
        frmDireccion.Show()
    End Sub

    Private Sub ConductorToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ConductorToolStripMenuItem.Click
        frmConductor.Show()
    End Sub

    Private Sub ProvinciaToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles ProvinciaToolStripMenuItem.Click
        frmProvincia.Show()
    End Sub

    Private Sub DetallePaqueteToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles DetallePaqueteToolStripMenuItem.Click
        frmDetalle_Paquete.Show()
    End Sub

    Private Sub BusToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles BusToolStripMenuItem.Click
        frmBus.Show()
    End Sub

    Private Sub BusConductorToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles BusConductorToolStripMenuItem.Click
        frmBusConductor.Show()
    End Sub

    Private Sub PaqueteToolStripMenuItem_Click(sender As Object, e As EventArgs) Handles PaqueteToolStripMenuItem.Click
        frmPaquete.Show()
    End Sub
End Class