implicit real*8(a-h,o-z)
integer, parameter :: nmax = 600
!12 variables: 2 reactantes en 2 dimensiones (x,y) colocados cada uno de ellos en 2 capas de fluido
real*8 a0l1(nmax),b0l1(nmax),a1l1(nmax),b1l1(nmax),a2l1(nmax),b2l1(nmax)
real*8 a0l2(nmax),b0l2(nmax),a1l2(nmax),b1l2(nmax),a2l2(nmax),b2l2(nmax)
!vectores que guardan la siguiente iteracion
real*8 a0l1p(nmax),b0l1p(nmax),a1l1p(nmax),b1l1p(nmax),a2l1p(nmax),b2l1p(nmax)
real*8 a0l2p(nmax),b0l2p(nmax),a1l2p(nmax),b1l2p(nmax),a2l2p(nmax),b2l2p(nmax)
!wave number,coupling coefficient between layers, velocity seen from the other layer, velocity of a reference system
real*8 k,u,v,vsr
real*8 dt,dx
integer itmax,iloc(1),it
real*8 delta
logical existe
character(len=256) :: output_dir
character(len=512) :: filename,ftime,fsigma
integer unit_out,tt,unit_out2

output_dir = '../data_experiments'
filename=trim(output_dir)//'/concentr_sist12acop.dat'
fsigma = trim('../data_temporal/sigma.dat')

k = 0.001
dk= 0.01
v=85.
da=1.
db=1./0.1
delta = da/db

!Parámetros
dx=1.
dt=0.001
itmax=int(600/dt)
trans = int(100/dt)
vsr=2.5
u=25.

open(newunit=unit_out2,file=fsigma,status='replace',action='write')

do ik=1,25

a0l1=0.;a0l2=0.;a1l1=0.;a1l2=0.;a2l1=0.;a2l2=0.
b0l1=1.;b0l2=1.;b1l1=0.;b1l2=0.;b2l1=0.;b2l2=0.

!Condiciones iniciales
do i=(nmax/4)+1,nmax
a0l1(i)=1.;a0l2(i)=1.
b0l1(i)=0.;b0l2(i)=0.
enddo
a1l1(nmax/4)= 0.001;a1l2(nmax/4)= 0.001
b1l1(nmax/4)=-0.001;b1l2(nmax/4)=-0.001

a0l1p=a0l1; b0l1p=b0l1; a1l1p=a1l1; b1l1p=b1l1; a2l1p=a2l1; b2l1p=b2l1
a0l2p=a0l2; b0l2p=b0l2; a1l2p=a1l2; b1l2p=b1l2; a2l2p=a2l2; b2l2p=b2l2

!variables para calculo de sigma
n=0
st=0.
sty=0.
st2=0.
sy=0.

ii=0


do it=1,itmax

do i=2,nmax-1
!Bloque de alpha - 1era capa
a0l1p(i) = a0l1(i) + dt*(da*(a0l1(i+1)+a0l1(i-1)-2.*a0l1(i))/(dx**2) &
                         - a0l1(i)*(b0l1(i)**2) &
                         + vsr*(a0l1(i+1)-a0l1(i-1))/(2*dx)&
                         + da*u*(a0l2(i)-a0l1(i)))

a1l1p(i) = a1l1(i) + dt*(da*(a1l1(i+1)+a1l1(i-1)-2.*a1l1(i))/(dx**2) &
                         - da*(k**2)*a1l1(i) &
                         - (v/2)*k*a2l1(i) &
                         + vsr*(a1l1(i+1)-a1l1(i-1))/(2*dx)&
                         - (b0l1(i)**2)*a1l1(i) &
                         - 2.*a0l1(i)*b0l1(i)*b1l1(i) &
                         + da*u*(a1l2(i)-a1l1(i)))

a2l1p(i) = a2l1(i) + dt*(da*(a2l1(i+1)+a2l1(i-1)-2.*a2l1(i))/(dx**2) &
                         - da*(k**2)*a2l1(i) &
                         + (v/2)*k*a1l1(i) &
                         + vsr*(a2l1(i+1)-a2l1(i-1))/(2*dx)&
                         - (b0l1(i)**2)*a2l1(i) &
                         - 2.*a0l1(i)*b0l1(i)*b2l1(i) &
                         + da*u*(a2l2(i)-a2l1(i))) 

!Bloque de beta - 1era capa
b0l1p(i) = b0l1(i) + dt*(db*(b0l1(i+1)+b0l1(i-1)-2.*b0l1(i))/(dx**2) &
                         + a0l1(i)*(b0l1(i)**2) &
                         + vsr*(b0l1(i+1)-b0l1(i-1))/(2*dx)&
                         + db*u*(b0l2(i)-b0l1(i)))

b1l1p(i) = b1l1(i) + dt*(db*(b1l1(i+1)+b1l1(i-1)-2.*b1l1(i))/(dx**2) &
                         - db*(k**2)*b1l1(i) &
                         - (v/2)*k*b2l1(i) &
                         + vsr*(b1l1(i+1)-b1l1(i-1))/(2*dx)&
                         + (b0l1(i)**2)*a1l1(i) &
                         + 2.*a0l1(i)*b0l1(i)*b1l1(i) &
                         + db*u*(b1l2(i)-b1l1(i)))

b2l1p(i) = b2l1(i) + dt*(db*(b2l1(i+1)+b2l1(i-1)-2.*b2l1(i))/(dx**2) &
                         - db*(k**2)*b2l1(i) &
                         + (v/2)*k*b1l1(i) &
                         + vsr*(b2l1(i+1)-b2l1(i-1))/(2*dx)&
                         + (b0l1(i)**2)*a2l1(i) &
                         + 2.*a0l1(i)*b0l1(i)*b2l1(i) &
                         + db*u*(b2l2(i)-b2l1(i)))

!Bloque de alpha - 2da capa  
a0l2p(i) = a0l2(i) + dt*(da*(a0l2(i+1)+a0l2(i-1)-2.*a0l2(i))/(dx**2) &
                         - a0l2(i)*(b0l2(i)**2) &
                         + vsr*(a0l2(i+1)-a0l2(i-1))/(2*dx)&
                         + da*u*(a0l1(i)-a0l2(i)))

a1l2p(i) = a1l2(i) + dt*(da*(a1l2(i+1)+a1l2(i-1)-2.*a1l2(i))/(dx**2) &
                         - da*(k**2)*a1l2(i) &
                         + (v/2)*k*a2l2(i) &
                         + vsr*(a1l2(i+1)-a1l2(i-1))/(2*dx)&
                         - (b0l2(i)**2)*a1l2(i) &
                         - 2.*a0l2(i)*b0l2(i)*b1l2(i) &
                         + da*u*(a1l1(i)-a1l2(i)))

a2l2p(i) = a2l2(i) + dt*(da*(a2l2(i+1)+a2l2(i-1)-2.*a2l2(i))/(dx**2) &
                         - da*(k**2)*a2l2(i) &
                         - (v/2)*k*a1l2(i) &
                         + vsr*(a2l2(i+1)-a2l2(i-1))/(2*dx)&
                         - (b0l2(i)**2)*a2l2(i) &
                         - 2.*a0l2(i)*b0l2(i)*b2l2(i) &
                         + da*u*(a2l1(i)-a2l2(i))) 

!Bloque de beta - 2da capa
b0l2p(i) = b0l2(i) + dt*(db*(b0l2(i+1)+b0l2(i-1)-2.*b0l2(i))/(dx**2) &
                         + a0l2(i)*(b0l2(i)**2) &
                         + vsr*(b0l2(i+1)-b0l2(i-1))/(2*dx)&
                         + db*u*(b0l1(i)-b0l2(i)))

b1l2p(i) = b1l2(i) + dt*(db*(b1l2(i+1)+b1l2(i-1)-2.*b1l2(i))/(dx**2) &
                         - db*(k**2)*b1l2(i) &
                         + (v/2)*k*b2l2(i) &
                         + vsr*(b1l2(i+1)-b1l2(i-1))/(2*dx)&
                         + (b0l2(i)**2)*a1l2(i) &
                         + 2.*a0l2(i)*b0l2(i)*b1l2(i) &
                         + db*u*(b1l1(i)-b1l2(i)))

b2l2p(i) = b2l2(i) + dt*(db*(b2l2(i+1)+b2l2(i-1)-2.*b2l2(i))/(dx**2) &
                         - db*(k**2)*b2l2(i) &
                         - (v/2)*k*b1l2(i) &
                         + vsr*(b2l2(i+1)-b2l2(i-1))/(2*dx)&
                         + (b0l2(i)**2)*a2l2(i) &
                         + 2.*a0l2(i)*b0l2(i)*b2l2(i) &
                         + db*u*(b2l1(i)-b2l2(i)))

enddo

!Actualización de variables
a0l1 = a0l1p; b0l1 = b0l1p; a1l1 = a1l1p; b1l1 = b1l1p; a2l1=a2l1p; b2l1=b2l1p
a0l2 = a0l2p; b0l2 = b0l2p; a1l2 = a1l2p; b1l2 = b1l2p; a2l2=a2l2p; b2l2=b2l2p

!Condiciones de frontera
a0l1(1)=0.;a0l1(nmax)=1.;a0l2(1)=0.;a0l2(nmax)=1.
b0l1(1)=1.;b0l1(nmax)=0.;b0l2(1)=1.;b0l2(nmax)=0.

a1l1(1)=0.;a1l1(nmax)=0.;a1l2(1)=0.;a1l2(nmax)=0.
b1l1(1)=0.;b1l1(nmax)=0.;b1l2(1)=0.;b1l2(nmax)=0.

a2l1(1)=0.;a2l1(nmax)=0.;a2l2(1)=0.;a2l2(nmax)=0.
b2l1(1)=0.;b2l1(nmax)=0.;b2l2(1)=0.;b2l2(nmax)=0.

!Guardo cada cierto tiempo
itst = mod(it,int(50*(1/dt)))
!ii=it*10/10000
if (itst.eq.0) then !

tt=int(it*dt)
write(ftime,'(A,I4.4,A)') '../data_temporal/t_', tt, '.dat'

open(newunit=unit_out,file=trim(ftime),status='replace', action='write')
do i=1,nmax
write(unit_out,*) i,a0l1(i),a0l2(i),a1l1(i),a1l2(i),a2l1(i),a2l2(i),b0l1(i),b0l2(i),b1l1(i),b1l2(i),b2l1(i),b2l2(i)
enddo
close(unit_out)
!write(*,*) ' '
endif

!Cálculo de tasa de decrecimiento
if ((mod(it,int(1./dt)).eq.0).and.(it.gt.trans)) then
n = n+1
t = it*dt
cmax=maxval(a1l1)
iloc = maxloc(a1l1)
ilc =iloc(1)
y = log(cmax)
st = st + t
sy = sy + y
sty = sty + t*y
st2 = st2 + t**2
!write(*,*) n,t,cmax,y
sigma = (n*sty-st*sy)/(n*st2-(st)**2)
write(*,*) t,sigma,cmax,ilc,y
write(unit_out2,*) t,sigma,y
endif 

enddo
sigma = (n*sty-st*sy)/(n*st2-(st)**2)
write(*,*) sigma, ilc

inquire(file=filename,exist=existe)
!Si existe lo abro y añado datos
if (existe) then
open(unit=23,file=filename,status='old',action='write',position='append')
!Si no existe se crea y escribe encabezados
else
open(unit=23,file=filename,status='new',action='write',position='append')
write(23,'(A)') &
'# k            sigma       delta     v        da        db' // &
'      vsr       u    t_trans   itmax    nmax    dt       dx '
endif

write(23,'(f8.4,1x,f14.8,1x,2(f8.3,1x),4(f8.3,1x),i6,1x,i10,1x,i6,1x,2(f8.5,1x))') &
k,sigma,delta,v,da,db,vsr,u,int(trans*dt),itmax,nmax,dt,dx
close(23)

k=k+dk
enddo
close(unit_out2)
end
